from datetime import datetime
from time import time

from bson import ObjectId
from utils.config import config
from utils.data.user import update_user_last_active_time
from utils.db import token_data_db, user_data_db
from utils.exceptions import TokenNotExistError, UIDNotExistError
from utils.hash import get_hash
from utils.time_helper import (
    get_datetime_after_hours,
    get_now_without_mileseconds,
)


def generate_token(uid: str) -> str:
    return get_hash(str(time()) + uid)


def is_uid_exist(uid: str) -> bool:
    return user_data_db.count_documents({"_id": ObjectId(uid)}) != 0


def is_token_exist(token: str) -> bool:
    return token_data_db.count_documents({"token": token}) != 0


def create_token(uid: str) -> str:
    if not uid:
        raise UIDNotExistError("UID 不能为空")

    if not is_uid_exist(uid):
        raise UIDNotExistError("UID 不存在")

    now_time: datetime = get_now_without_mileseconds()
    token: str = generate_token(uid)
    token_data_db.insert_one(
        {
            "create_time": now_time,
            "expire_time": get_datetime_after_hours(
                now_time, offset=config.token_expire_hours
            ),
            "user": {
                "id": uid,
            },
            "token": token,
        }
    )
    return token


def update_token_expire_time(token: str) -> None:
    token_data = token_data_db.find_one({"token": token})
    if not token_data:
        raise TokenNotExistError("Token 不存在或已过期")

    token_data_db.update_one(
        {"token": token},
        {
            "$set": {
                "expire_time": get_datetime_after_hours(
                    get_now_without_mileseconds(),
                    offset=config.token_expire_hours,
                ),
            },
        },
    )


def verify_token(token: str) -> str:
    if token is None:
        raise TokenNotExistError("Token 不能为空")

    token_data = token_data_db.find_one({"token": token})
    if not token_data:
        raise TokenNotExistError("Token 不存在或已过期")
    uid: str = token_data["user"]["id"]
    update_token_expire_time(token)
    update_user_last_active_time(uid)
    return uid


def expire_token(token: str) -> None:
    if token is None:
        raise TokenNotExistError("Token 不能为空")

    if not is_token_exist(token):
        raise TokenNotExistError("Token 不存在或已过期")
    token_data_db.delete_one({"token": token})
