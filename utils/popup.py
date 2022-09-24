from time import sleep

from pywebio.output import close_popup, popup, put_buttons
from pywebio.pin import pin, put_input

from utils.callback import bind_enter_key_callback
from utils.data.user import log_in
from utils.exceptions import (PasswordIlliegalError, UsernameIlliegalError,
                              UsernameOrPasswordWrongError)
from utils.page import get_url_to_module, jump_to
from utils.widgets import toast, toast_error_and_return, toast_warn_and_return

_login_finished: bool = False
_uid: str = ""


def login_popup() -> str:
    popup(
        title="登录",
        content=[
            put_input("user_name", "text", label="用户名"),
            put_input("password", "password", label="密码"),
            put_buttons(
                buttons=[
                    {"label": "登录", "value": "login", "color": "success"},
                    {"label": "注册", "value": "signup"}
                ],
                onclick=[
                    on_login_button_clicked,
                    on_signup_button_clicked
                ]
            )
        ],
        size="large",
        closable=False
    )
    bind_enter_key_callback("password", on_enter_key_pressed)

    while not _login_finished:
        sleep(0.3)
    return _uid


def on_enter_key_pressed(_) -> None:
    on_login_button_clicked()


def on_login_button_clicked() -> None:
    global _login_finished
    global _uid
    user_name: str = pin.user_name
    password: str = pin.password

    try:
        _uid = log_in(user_name, password)
    except UsernameIlliegalError:
        toast_warn_and_return("请输入用户名")
    except PasswordIlliegalError:
        toast_warn_and_return("请输入密码")
    except UsernameOrPasswordWrongError:
        toast_error_and_return("用户名或密码错误")
    else:
        toast("登录成功", color="success")
        close_popup()
        _login_finished = True


def on_signup_button_clicked() -> None:
    jump_to(get_url_to_module("signin"))
