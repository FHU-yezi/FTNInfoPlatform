from datetime import datetime, timedelta
from hashlib import sha256
from time import time

from utils.config import config
from utils.db import cookie_data_db, user_data_db


def get_hash(text: str) -> str:
    return sha256(text.encode("utf-8")).hexdigest()


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

    cookie_data_db.insert_one({
        "create_time": now_time,
        "expire_time": now_time + timedelta(
            seconds=config.cookie_expire_seconds
        ),
        "uid": user_data["_id"],
        "cookie": cookie
    })

    return cookie


def check_cookie(cookie: str) -> bool:
    cookie_data = cookie_data_db.find({"cookie": cookie})
    if not cookie_data:  # 没有对应的 Cookie
        return False
    else:
        cookie_data["expire_time"] = (
            datetime.now() + timedelta(seconds=config.cookie_expire_seconds)
        )
        # 顺延 Cookie 有效期
        cookie_data_db.update_one(
            {"_id": cookie_data["_id"]},
            {"$set": cookie_data}
        )
        return False


def expire_cookie(cookie: str) -> bool:
    cookie_data = cookie_data_db.find({"cookie": cookie})
    if not cookie_data:  # 没有对应的 Cookie
        return False
    else:
        cookie_data_db.delete_one({"_id": cookie_data["_id"]})
        return True
