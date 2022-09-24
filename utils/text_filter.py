from typing import Set
from re import compile


BANNED_CHARS: Set[str] = {
    " ",
    "\\",
    ";",
    "^",
    "$",
}
USER_NAME_ILLIEGAL_CHARS: Set[str] = {
    " ", "!", "@", "#",
    "\\", "$", "%", "^",
    "/", "&", "*", "|",
    ":", "<", ">", ",",
    ";", ".", "?", "`",
    "[", "~", "！", "，",
    "]", "。", "？", "(",
    ")", "-", "=", "：",
    "；", "、", "￥"
}
# 至少为八个字符，包含一个字母和一个数字
PASSWORD_RE = compile(r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$")


def is_illiegal_user_name(user_name: str) -> bool:
    for char in user_name:
        if char in USER_NAME_ILLIEGAL_CHARS:
            return True
    return False


def is_illiegal_password(password: str) -> bool:
    # 判断是否包含空格
    if " " in password:
        return True
    for char in password:
        # 判断是否包含中文
        if '\u4e00' <= char <= '\u9fff':
            return True
    return False


def is_weak_password(password: str) -> bool:
    if not PASSWORD_RE.fullmatch(password):
        return True
    return False


def has_banned_chars(text: str) -> bool:
    for char in text:
        if char in BANNED_CHARS:
            return True
    return False


def input_filter(text: str) -> str:
    for char in BANNED_CHARS:
        text = text.replace(char, "")
    return text
