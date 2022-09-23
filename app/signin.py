from time import sleep

from pywebio.output import put_buttons, put_markdown, toast, use_scope
from pywebio.pin import pin, put_input
from utils.auth import signup
from utils.page import get_base_url, jump_to
from utils.widgets import toast_error_and_return, toast_warn_and_return

NAME: str = "用户注册"
DESC: str = "注册新用户"
VISIBILITY: bool = False


def on_signup_button_clicked() -> None:
    user_name: str = pin.user_name
    passowrd: str = pin.password
    passowrd_again: str = pin.password_again

    if not user_name or not passowrd or not passowrd_again:
        toast_warn_and_return("请输入用户名和密码")

    if passowrd != passowrd_again:
        toast_warn_and_return("两次输入的密码不匹配")

    try:
        signup(user_name, passowrd)
    except ValueError:
        toast_error_and_return("该用户名已被占用")
    except Exception:  # TODO
        toast_error_and_return("用户名或密码中含有不合法字符")
    else:
        toast("注册成功", color="success")

    # 将按钮设为不可用
    # TODO
    with use_scope("buttons", clear=True):
        put_buttons(
            buttons=[
                {"label": "注册成功", "value": "publish", "color": "success", "disabled": True},
                {"label": "取消", "value": "cancel"}
            ],
            onclick=[
                on_signup_button_clicked,
                on_cancel_button_clicked
            ]
        )

    sleep(1)
    jump_to(get_base_url())


def on_cancel_button_clicked() -> None:
    jump_to(get_base_url())


def signin() -> None:
    put_markdown("# 用户注册")

    put_input("user_name", "text", label="用户名")
    put_input("password", "password", label="密码")
    put_input("password_again", "password", label="确认密码")

    with use_scope("buttons", clear=True):
        put_buttons(
            buttons=[
                {"label": "注册", "value": "publish", "color": "success"},
                {"label": "取消", "value": "cancel"}
            ],
            onclick=[
                on_signup_button_clicked,
                on_cancel_button_clicked
            ]
        )
