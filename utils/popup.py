from time import sleep

from pywebio.output import close_popup, popup, put_buttons
from pywebio.pin import pin, put_input

from utils.auth import login
from utils.callback import bind_enter_key_callback
from utils.page import get_base_url, jump_to
from utils.widgets import toast, toast_error_and_return, toast_warn_and_return

_login_finished: bool = False


def login_popup() -> None:
    popup(
        title="用户登录",
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


def on_enter_key_pressed(_) -> None:
    on_login_button_clicked()


def on_login_button_clicked() -> None:
    global _login_finished
    user_name: str = pin.user_name
    password: str = pin.password

    if not user_name or not password:
        toast_warn_and_return("请输入用户名和密码")

    if login(user_name, password):
        toast("登录成功", color="success")
        close_popup()
        _login_finished = True
    else:
        toast_error_and_return("用户名或密码错误")


def on_signup_button_clicked() -> None:
    jump_to(get_base_url() + "?app=signin")
