from datetime import datetime
from time import time
from typing import Any, Dict, List, Sequence

from bson import ObjectId

from utils.config import config
from utils.db import token_data_db
from utils.dict_helper import flatten_dict, get_reversed_dict
from utils.exceptions import TokenNotExistError
from utils.hash import get_hash
from utils.time_helper import (
    get_datetime_after_hours,
    get_now_without_mileseconds,
)


def generate_token(uid: str) -> str:
    return get_hash(str(time()) + uid)


class Token:
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
    def object_id(self) -> ObjectId:
        return ObjectId(self.id)

    @property
    def is_expired(self) -> bool:
        return self.expire_time < datetime.now()

    @property
    def user(self):
        from data.user import User

        return User.from_id(self.user_id)

    @classmethod
    def from_id(cls, id: str) -> "Token":
        db_data = token_data_db.find_one({"_id": ObjectId(id)})
        if not db_data:
            raise TokenNotExistError
        return cls.from_db_data(db_data)

    @classmethod
    def from_db_data(cls, db_data: Dict) -> "Token":
        # 展平数据库查询结果
        db_data = flatten_dict(db_data)
        db_data["_id"] = str(db_data["_id"])

        data_to_init_func: Dict[str, Any] = {}
        for k, v in db_data.items():
            attr_name = cls.db_key_attr_mapping.get(k)
            if not attr_name:  # 数据库中存在，但模型中未定义的字段
                continue  # 跳过
            data_to_init_func[attr_name] = v

        # 调用 __init__ 初始化对象
        return cls(**data_to_init_func)

    @classmethod
    def from_token_value(cls, token_value: str) -> "Token":
        # 调用此方法的 Token 值可能为空字符串
        # 先进行判断再查询数据库
        if not token_value:
            raise TokenNotExistError

        db_data = token_data_db.find_one({"token": token_value})
        if not db_data:
            raise TokenNotExistError("Token 不存在或已过期")

        return cls.from_db_data(db_data)

    def __eq__(self, __o: Any) -> bool:
        if self.__class__ != __o.__class__:
            return False

        return self.id == __o.id

    def __setattr__(self, __name: str, __value: Any) -> None:
        # 由于脏属性列表在 __init__ 函数的末尾，当该列表存在时
        # 证明 __init__ 过程已完成
        init_finished: bool = hasattr(self, "_dirty")

        # __init__ 已完成，禁止设置模型中未定义的属性
        if init_finished and not hasattr(self, __name):
            raise Exception(f"不能设置模型中未定义的属性 {__name}")

        # 如果脏属性列表存在，且该属性未被标脏，则将该属性标脏
        if init_finished and __name not in self._dirty:
            self._dirty.append(__name)
        # 设置属性值
        super().__setattr__(__name, __value)

    def sync(self) -> None:
        data_to_update = {}
        # 遍历脏数据列表
        for attr in self._dirty:
            db_key: str = self.__class__.attr_db_key_mapping[attr]
            data_to_update[db_key] = getattr(self, attr)

        # 更新数据库中的信息
        token_data_db.update_one({"_id": self.object_id}, {"$set": data_to_update})
        # 清空脏数据列表
        self._dirty.clear()

    def sync_only(self, attr_list: Sequence[str]) -> None:
        data_to_update = {}
        for attr in attr_list:
            if attr not in self._dirty:
                raise Exception(f"{attr} 未被标记为脏数据")
            db_key: str = self.__class__.attr_db_key_mapping[attr]
            data_to_update[db_key] = getattr(self, attr)

            # 从脏数据列表中删除对应属性名
            self._dirty.remove(attr)

        # 更新数据库中的信息
        token_data_db.update_one({"_id": self.object_id}, {"$set": data_to_update})

    def sync_all(self) -> None:
        data_to_update = {}
        for attr, db_key in self.__class__.attr_db_key_mapping.items():
            data_to_update[db_key] = getattr(self, attr)

        # 更新数据库中的信息
        token_data_db.update_one({"_id": self.object_id}, {"$set": data_to_update})
        # 清空脏数据列表
        self._dirty.clear()

    def remove(self) -> None:
        token_data_db.delete_one({"_id": self.object_id})

    @classmethod
    def create(cls, user_obj) -> "Token":
        now_time: datetime = get_now_without_mileseconds()
        token: str = generate_token(user_obj.id)
        insert_result = token_data_db.insert_one(
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

        token_data_db.delete_one({"token": self.value})
