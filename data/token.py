from datetime import datetime
from time import time
from typing import Dict, List

from bson import ObjectId

from data._base import DataModel
from utils.config import config
from utils.db import token_data_db
from utils.dict_helper import get_reversed_dict
from utils.exceptions import TokenNotExistError
from utils.hash import get_hash
from utils.time_helper import (
    get_datetime_after_hours,
    get_now_without_mileseconds,
)


def generate_token(uid: str) -> str:
    return get_hash(str(time()) + uid)


class Token(DataModel):
    db = token_data_db
    attr_db_key_mapping: Dict[str, str] = {
        "id": "_id",
        "create_time": "create_time",
        "expire_time": "expire_time",
        "user_id": "user.id",
        "value": "token",
    }
    db_key_attr_mapping = get_reversed_dict(attr_db_key_mapping)

    def __init__(
        self,
        id: str,
        create_time: datetime,
        expire_time: datetime,
        user_id: str,
        value: str,
    ) -> None:
        self.id = id
        self.create_time = create_time
        self.expire_time = expire_time
        self.user_id = user_id
        self.value = value

        # 脏属性列表必须在其它属性设置后再被创建
        self._dirty: List[str] = []

    @property
    def is_expired(self) -> bool:
        return self.expire_time < datetime.now()

    @property
    def user(self):
        from data.user import User

        return User.from_id(self.user_id)

    @classmethod
    def from_id(cls, id: str) -> "Token":
        db_data = cls.db.find_one({"_id": ObjectId(id)})
        if not db_data:
            raise TokenNotExistError
        return cls.from_db_data(db_data)

    @classmethod
    def from_token_value(cls, token_value: str) -> "Token":
        # 调用此方法的 Token 值可能为空字符串
        # 先进行判断再查询数据库
        if not token_value:
            raise TokenNotExistError

        db_data = cls.db.find_one({"token": token_value})
        if not db_data:
            raise TokenNotExistError("Token 不存在或已过期")

        return cls.from_db_data(db_data)

    @classmethod
    def create(cls, user_obj) -> "Token":
        now_time: datetime = get_now_without_mileseconds()
        token: str = generate_token(user_obj.id)
        insert_result = cls.db.insert_one(
            {
                "create_time": now_time,
                "expire_time": get_datetime_after_hours(
                    now_time, offset=config.token_expire_hours
                ),
                "user": {
                    "id": user_obj.id,
                },
                "token": token,
            }
        )

        # 返回新创建的 Token 对象
        return cls.from_id(insert_result.inserted_id)

    def update_expire_time(self) -> None:
        if self.is_expired:
            raise TokenNotExistError("Token 不存在或已过期")

        self.expire_time = get_datetime_after_hours(
            get_now_without_mileseconds(),
            config.token_expire_hours,
        )
        self.sync()

    def expire(self) -> None:
        # 将过期时间设为现在，不会更新到数据库，
        # 但可以使 self.is_expired 返回 True
        self.expire_time = get_now_without_mileseconds()

        self.db.delete_one({"token": self.value})
