from datetime import datetime
from typing import Any, Dict, List, Literal, Optional, Sequence

from bson import ObjectId
from httpx import get as httpx_get

from utils.db import user_data_db
from utils.dict_helper import flatten_dict, get_reversed_dict
from utils.exceptions import (
    DuplicatedUsernameError,
    DuplicatedUserURLError,
    JianshuAlreadyBindedError,
    PasswordIlliegalError,
    PasswordNotEqualError,
    UIDNotExistError,
    UsernameIlliegalError,
    UsernameNotChangedError,
    UsernameOrPasswordWrongError,
    UserURLIlliegalError,
    WeakPasswordError,
)
from utils.hash import check_password, encrypt_password
from utils.text_filter import (
    is_illiegal_password,
    is_illiegal_user_name,
    is_weak_password,
)
from utils.time_helper import get_now_without_mileseconds


def is_user_name_exist(user_name: str) -> bool:
    return (
        user_data_db.count_documents(
            {"user_name": user_name},
        )
        != 0
    )


def is_jianshu_url_exist(jianshu_url: str) -> bool:
    return (
        user_data_db.count_documents(
            {"jianshu.url": jianshu_url},
        )
        != 0
    )


def get_user_jianshu_name(user_url: str) -> str:
    if not user_url.startswith("https://www.jianshu.com/u/"):
        raise UserURLIlliegalError("用户个人主页 URL 格式错误")
    try:
        data = httpx_get(
            "https://www.jianshu.com/asimov/users/slug/" + user_url.split("/")[4]
        ).json()
        return data["nickname"]
    except Exception:
        raise UserURLIlliegalError("获取数据时出现异常")


class User:
    attr_db_key_mapping: Dict[str, str] = {
        "id": "_id",
        # TODO: 去除数据库中多余的 signin_time 字段
        "signup_time": "signup_time",
        "last_active_time": "last_active_time",
        "name": "user_name",
        "encrypted_password": "password",
        "permission_admin": "permissions.admin",
        "permission_user": "permissions.user",
        "jianshu_url": "jianshu.url",
        "jianshu_name": "jianshu.name",
    }
    db_key_attr_mapping = get_reversed_dict(attr_db_key_mapping)

    def __init__(
        self,
        id: str,
        signup_time: datetime,
        last_active_time: datetime,
        name: str,
        encrypted_password: str,
        permission_admin: int,
        permission_user: int,
        jianshu_url: Optional[str],
        jianshu_name: Optional[str],
    ) -> None:
        self.id = id
        self.signup_time = signup_time
        self.last_active_time = last_active_time
        self.name = name
        self.encrypted_password = encrypted_password
        self.permission_admin = permission_admin
        self.permission_user = permission_user
        self.jianshu_url = jianshu_url
        self.jianshu_name = jianshu_name

        # 脏属性列表必须在其它属性设置后再被创建
        self._dirty: List[str] = []

    @property
    def object_id(self) -> ObjectId:
        return ObjectId(self.id)

    def is_dirty(self, attr_name: str) -> bool:
        if not hasattr(self, attr_name):
            raise AttributeError(f"属性 {attr_name} 不存在")
        return attr_name in self._dirty

    @classmethod
    def from_id(cls, id: str) -> "User":
        db_data = user_data_db.find_one({"_id": ObjectId(id)})
        if not db_data:
            raise UIDNotExistError
        return cls.from_db_data(db_data)

    @classmethod
    def from_db_data(cls, db_data: Dict) -> "User":
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
        user_data_db.update_one({"_id": self.object_id}, {"$set": data_to_update})
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
        user_data_db.update_one({"_id": self.object_id}, {"$set": data_to_update})

    def sync_all(self) -> None:
        data_to_update = {}
        for attr, db_key in self.__class__.attr_db_key_mapping.items():
            data_to_update[db_key] = getattr(self, attr)

        # 更新数据库中的信息
        user_data_db.update_one({"_id": self.object_id}, {"$set": data_to_update})
        # 清空脏数据列表
        self._dirty.clear()

    def delete(self) -> None:
        user_data_db.delete_one({"_id": self.object_id})

    @property
    def buy_order(self):
        from data.order_new import Order

        db_data = user_data_db.find_one(
            {
                "order.type": "buy",
                "user.id": self.object_id,
            },
        )
        if db_data:
            return Order.from_db_data(db_data)

    @property
    def sell_order(self):
        from data.order_new import Order

        db_data = user_data_db.find_one(
            {
                "order.type": "sell",
                "user.id": self.object_id,
            },
        )
        if db_data:
            return Order.from_db_data(db_data)

    def finished_orders(self, order_type: Literal["buy", "sell"], limit: int) -> List:
        from utils.db import order_data_db

        data_list: List[Dict] = order_data_db.find(
            {
                "status": 1,  # 已完成
                "order.type": order_type,
                "user.id": self.id,
            }
        ).limit(limit)
        if not data_list:
            return []

        from data.order_new import Order

        return [Order.from_db_data(item) for item in data_list]

    @property
    def tokens(self):
        from utils.db import token_data_db

        data_list: List[Dict] = token_data_db.find(
            {"user.id": self.id},
        )
        if not data_list:
            return []

        from data.token_new import Token

        return [Token.from_db_data(item) for item in data_list]

    def expire_all_tokens(self) -> None:
        tokens: List = self.tokens

        for token in tokens:
            token.expire()

    @property
    def is_jianshu_binded(self) -> bool:
        return bool(self.jianshu_url)

    def update_last_active_time(self) -> None:
        self.last_active_time = get_now_without_mileseconds()
        self.sync_only(["last_active_time"])

    @classmethod
    def signup(
        cls,
        user_name: str,
        password: str,
        password_again: str,
        admin_permission_level: int,
        user_permission_level: int,
    ) -> "User":
        if password != password_again:
            raise PasswordNotEqualError("两次输入的密码不一致")
        if not 0 <= admin_permission_level <= 5:
            raise TypeError("参数 admin_permissions_level 必须介于 0 - 5 之间")
        if not 0 <= user_permission_level <= 5:
            raise TypeError("参数 user_permissions_level 必须介于 0 - 5 之间")

        if not user_name:
            raise UsernameIlliegalError("用户名不能为空")
        if not password:
            raise PasswordIlliegalError("密码不能为空")
        if is_illiegal_user_name(user_name):
            raise UsernameIlliegalError("用户名不合法")
        if is_illiegal_password(password):
            raise PasswordIlliegalError("密码不合法")
        if is_weak_password(password):
            raise WeakPasswordError("密码强度不足")

        if is_user_name_exist(user_name):
            raise DuplicatedUsernameError("用户名重复")

        now_time = get_now_without_mileseconds()
        encrypted_password: str = encrypt_password(password)
        insert_result = user_data_db.insert_one(
            {
                "signup_time": now_time,
                "last_active_time": now_time,
                "user_name": user_name,
                "password": encrypted_password,
                "permissions": {
                    "admin": admin_permission_level,
                    "user": user_permission_level,
                },
                "jianshu": {
                    "url": None,
                    "name": None,
                },
            }
        )

        # 返回新注册的用户对象
        return cls.from_id(insert_result.inserted_id)

    @classmethod
    def login(cls, user_name: str, password: str) -> "User":
        if not user_name:
            raise UsernameIlliegalError("用户名不能为空")
        if not password:
            raise PasswordIlliegalError("密码不能为空")

        db_data = user_data_db.find_one(
            {"user_name": user_name},
        )

        if not db_data:  # 未查询到相应记录
            raise UsernameOrPasswordWrongError("用户名或密码错误")

        if not check_password(password, db_data["password"]):  # 密码不匹配
            raise UsernameOrPasswordWrongError("用户名或密码错误")

        return cls.from_db_data(db_data)

    def change_name(self, new_name: str) -> None:
        if not new_name:
            raise UsernameIlliegalError("用户名不能为空")
        if is_illiegal_user_name(new_name):
            raise UsernameIlliegalError("用户名不合法")

        if is_user_name_exist(new_name):
            raise DuplicatedUsernameError("用户名重复")

        if self.name == new_name:
            raise UsernameNotChangedError("新昵称不能与旧昵称相同")

        self.name = new_name
        self.sync()

    def change_password(
        self, old_password: str, new_password: str, new_password_again: str
    ) -> None:
        if not old_password or not new_password:
            raise PasswordIlliegalError("密码不能为空")
        if is_illiegal_password(new_password):
            raise PasswordIlliegalError("密码不合法")
        if is_weak_password(new_password):
            raise WeakPasswordError("密码强度不足")
        if new_password != new_password_again:
            raise PasswordNotEqualError("两次输入的密码不一致")

        if not check_password(old_password, self.encrypted_password):
            raise UsernameOrPasswordWrongError("旧密码错误")

        encrypted_new_password: str = encrypt_password(new_password)

        self.encrypted_password = encrypted_new_password
        self.sync()

        # 过期用户的所有 Token
        self.expire_all_tokens()

    def bind_jianshu_account(self, jianshu_url: str) -> None:
        if not jianshu_url:
            raise UserURLIlliegalError("用户个人主页 URL 不能为空")

        # 正常情况下，绑定简书账号后对应入口会消失，不存在重复绑定的可能性
        # 此处仅做兜底处理
        if self.is_jianshu_binded:
            raise JianshuAlreadyBindedError("该用户已绑定简书个人主页 URL")

        if is_jianshu_url_exist(jianshu_url):
            raise DuplicatedUserURLError("该个人主页 URL 已被绑定")

        # 此处如果在获取简书昵称时发生异常，错误会向上传递
        jianshu_name = get_user_jianshu_name(jianshu_url)

        self.jianshu_url = jianshu_url
        self.jianshu_name = jianshu_name
        self.sync()

    def generate_token(self):
        from data.token_new import Token

        return Token.create(self)
