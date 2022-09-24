from typing import Dict

from bson import ObjectId
from utils.db import user_data_db
from utils.exceptions import (DuplicatedUsernameError, PasswordIlliegalError,
                              UIDNotExistError, UsernameIlliegalError,
                              UsernameOrPasswordWrongError, WeakPasswordError)
from utils.hash import get_hash
from utils.text_filter import (is_illiegal_password, is_illiegal_user_name,
                               is_weak_password)
from utils.time_helper import get_now_without_mileseconds


def is_user_name_exist(user_name: str) -> bool:
    return user_data_db.count_documents({"user_name": user_name}) != 0


def get_user_data_from_uid(uid: str) -> Dict:
    result: Dict = user_data_db.find_one({"_id": ObjectId(uid)})
    if not result:
        raise UIDNotExistError("UID 不存在")
    return result


def sign_up(user_name: str, password: str, admin_permissions_level: int,
            user_permissions_level: int) -> None:
    if not 0 <= admin_permissions_level <= 5:
        raise TypeError("参数 admin_permissions_level 必须介于 0 - 5 之间")
    if not 0 <= user_permissions_level <= 5:
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

    hashed_password: str = get_hash(password)
    user_data_db.insert_one({
        "signin_time": get_now_without_mileseconds(),
        "last_active_time": get_now_without_mileseconds(),
        "user_name": user_name,
        "password": hashed_password,
        "permissions": {
            "admin": admin_permissions_level,
            "user": user_permissions_level
        }
    })


def log_in(user_name: str, password: str) -> str:
    if not user_name:
        raise UsernameIlliegalError("用户名不能为空")
    if not password:
        raise PasswordIlliegalError("密码不能为空")

    hashed_password: str = get_hash(password)
    user_data = user_data_db.count_documents({
        "user_name": user_name, "password": hashed_password
    })
    if not user_data:  # 未查询到相应记录
        raise UsernameOrPasswordWrongError("用户名或密码错误")
    return str(user_data["_id"])
