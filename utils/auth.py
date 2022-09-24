from datetime import datetime, timedelta
from hashlib import sha256
from time import time
from utils.text_filter import has_banned_chars

from utils.config import config
from utils.db import token_data_db, user_data_db


def get_hash(text: str) -> str:
    return sha256(text.encode("utf-8")).hexdigest()[:15]


def generate_cookie(user_name: str, hashed_password: str) -> str:
    return get_hash(str(time()) + user_name + hashed_password)


def login(user_name: str, password: str) -> bool:
    hashed_password = get_hash(password)

    if user_data_db.count_documents(
        {"user_name": user_name, "password": hashed_password}
    ) == 1:
        return True
    else:
        return False


def signup(user_name: str, password: str) -> None:
    # TODO
    if has_banned_chars(user_name) or has_banned_chars(password):
        raise Exception("用户名或密码中含有不合法字符")

    if user_data_db.count_documents({"user_name": user_name}) != 0:
        raise ValueError("该用户已注册")

    hashed_password: str = get_hash(password)

    user_data_db.insert_one({
        "signin_time": datetime.now(),
        "user_name": user_name,
        "password": hashed_password
    })


def new_cookie(user_name: str, password: str) -> str:
    now_time = datetime.now()
    hashed_password = get_hash(password)
    cookie = generate_cookie(user_name, hashed_password)
    user_data = user_data_db.find_one({"user_name": user_name})

    token_data_db.insert_one({
        "create_time": now_time,
        "expire_time": now_time + timedelta(
            seconds=config.cookie_expire_seconds
        ),
        "user": {
            "id": user_data["_id"]
        },
        "cookie": cookie
    })

    return cookie


def check_cookie(cookie: str) -> bool:
    if not cookie:  # Cookie 字符串为空
        return False

    cookie_data = token_data_db.find_one({"cookie": cookie})
    if not cookie_data:  # 没有对应的 Cookie
        return False
    else:
        cookie_data["expire_time"] = (
            datetime.now() + timedelta(seconds=config.cookie_expire_seconds)
        )
        # 顺延 Cookie 有效期
        token_data_db.update_one(
            {"_id": cookie_data["_id"]},
            {"$set": cookie_data}
        )
        return True


def expire_cookie(cookie: str) -> bool:
    cookie_data = token_data_db.find_one({"cookie": cookie})
    if not cookie_data:  # 没有对应的 Cookie
        return False
    else:
        token_data_db.delete_one({"_id": cookie_data["_id"]})
        return True


def get_uid_from_cookie(cookie: str) -> str:
    result = token_data_db.find_one({"cookie": cookie})
    if not result:
        return ""
    else:
        return result["user"]["id"]
