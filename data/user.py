from typing import Dict

from bson import ObjectId
from httpx import get as httpx_get
from utils.db import user_data_db
from utils.exceptions import (
    DuplicatedUsernameError,
    DuplicatedUserURLError,
    PasswordIlliegalError,
    PasswordNotChangedError,
    PasswordNotEqualError,
    UIDNotExistError,
    UsernameIlliegalError,
    UsernameNotChangedError,
    UsernameNotExistError,
    UsernameOrPasswordWrongError,
    UserURLIlliegalError,
    WeakPasswordError,
)
from utils.hash import get_hash
from utils.text_filter import (
    is_illiegal_password,
    is_illiegal_user_name,
    is_weak_password,
)
from utils.time_helper import get_now_without_mileseconds


def get_user_jianshu_name(user_url: str) -> str:
    if not user_url.startswith("https://www.jianshu.com/u/"):
        raise UserURLIlliegalError("用户个人主页 URL 格式错误")
    try:
        response = httpx_get("https://www.jianshu.com/asimov/users/slug/" + user_url.split("/")[4])
        data = response.json()
        return data["nickname"]
    except Exception:
        raise UserURLIlliegalError("获取数据时出现异常")


def is_user_name_exist(user_name: str) -> bool:
    return user_data_db.count_documents({"user_name": user_name}) != 0


def is_jianshu_url_exist(jianshu_url: str) -> bool:
    return user_data_db.count_documents({"jianshu.url": jianshu_url}) != 0


def get_user_data_from_uid(uid: str) -> Dict:
    result: Dict = user_data_db.find_one({"_id": ObjectId(uid)})
    if not result:
        raise UIDNotExistError("UID 不存在")
    return result


def get_uid_from_user_name(user_name: str) -> str:
    result: Dict = user_data_db.find_one({"user_name": user_name})
    if not result:
        raise UsernameNotExistError("用户名不存在")
    return str(result["_id"])


def sign_up(
    user_name: str,
    password: str,
    password_again: str,
    admin_permissions_level: int,
    user_permissions_level: int,
) -> str:
    if password != password_again:
        raise PasswordNotEqualError("两次输入的密码不一致")
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

    now_time = get_now_without_mileseconds()
    hashed_password: str = get_hash(password)
    user_data_db.insert_one(
        {
            "signup_time": now_time,
            "last_active_time": now_time,
            "user_name": user_name,
            "password": hashed_password,
            "permissions": {
                "admin": admin_permissions_level,
                "user": user_permissions_level,
            },
            "jianshu": {
                "url": None,
                "name": None,
            }
        }
    )

    # 返回新注册的用户的 UID
    uid: str = get_uid_from_user_name(user_name)
    return uid


def log_in(user_name: str, password: str) -> str:
    if not user_name:
        raise UsernameIlliegalError("用户名不能为空")
    if not password:
        raise PasswordIlliegalError("密码不能为空")

    hashed_password: str = get_hash(password)
    user_data = user_data_db.find_one(
        {
            "user_name": user_name,
            "password": hashed_password,
        }
    )
    if not user_data:  # 未查询到相应记录
        raise UsernameOrPasswordWrongError("用户名或密码错误")

    uid: str = str(user_data["_id"])
    update_user_last_active_time(uid)
    return uid


def update_user_last_active_time(uid: str) -> None:
    user_data = user_data_db.find_one({"_id": ObjectId(uid)})
    if not user_data:
        raise UIDNotExistError("UID 不存在")

    data_to_update: Dict = {
        "last_active_time": get_now_without_mileseconds(),
    }
    user_data_db.update_one(
        {"_id": ObjectId(uid)},
        {"$set": data_to_update},
    )


def change_user_name(uid: str, new_user_name: str) -> None:
    if not new_user_name:
        raise UsernameIlliegalError("用户名不能为空")
    if is_illiegal_user_name(new_user_name):
        raise UsernameIlliegalError("用户名不合法")

    if is_user_name_exist(new_user_name):
        raise DuplicatedUsernameError("用户名重复")

    user_data = user_data_db.find_one({"_id": ObjectId(uid)})
    if not user_data:
        raise UIDNotExistError("UID 不存在")
    old_user_name: str = user_data["user_name"]
    if old_user_name == new_user_name:
        raise UsernameNotChangedError("新昵称不能与旧昵称相同")

    data_to_update: Dict = {
        "user_name": new_user_name,
    }
    user_data_db.update_one(
        {"_id": ObjectId(uid)},
        {"$set": data_to_update},
    )


def change_password(
    uid: str, old_password: str, new_password: str, new_password_again: str
) -> None:
    if not old_password or not new_password:
        raise PasswordIlliegalError("密码不能为空")
    if is_illiegal_password(new_password):
        raise PasswordIlliegalError("密码不合法")
    if is_weak_password(new_password):
        raise WeakPasswordError("密码强度不足")
    if new_password != new_password_again:
        raise PasswordNotEqualError("两次输入的密码不一致")

    user_data = user_data_db.find_one({"_id": ObjectId(uid)})
    if not user_data:
        raise UIDNotExistError("UID 不存在")
    hashed_old_password: str = get_hash(old_password)
    if user_data["password"] != hashed_old_password:
        raise UsernameOrPasswordWrongError("旧密码错误")
    hashed_new_password: str = get_hash(new_password)
    if hashed_old_password == hashed_new_password:
        raise PasswordNotChangedError("新密码不能与旧密码相同")

    data_to_update: Dict = {
        "password": hashed_new_password,
    }
    user_data_db.update_one(
        {"_id": ObjectId(uid)},
        {"$set": data_to_update},
    )

    # 将用户当前的 Token 过期，该部分由调用方完成


def bind_jianshu_account(uid: str, jianshu_url: str) -> str:
    if not jianshu_url:
        raise UserURLIlliegalError("用户个人主页 URL 不能为空")
    user_data = user_data_db.find_one({"_id": ObjectId(uid)})
    if not user_data:
        raise UIDNotExistError("UID 不存在")

    if is_jianshu_url_exist(jianshu_url):
        raise DuplicatedUserURLError("该个人主页 URL 已被绑定")

    # 此处可能发生错误的向上传递
    jianshu_name = get_user_jianshu_name(jianshu_url)

    data_to_update: Dict = {
        "jianshu": {
            "url": jianshu_url,
            "name": jianshu_name,
        }
    }
    user_data_db.update_one(
        {"_id": ObjectId(uid)},
        {"$set": data_to_update}
    )
    return jianshu_name
