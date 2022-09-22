from pywebio.output import popup, put_button, close_popup
from pywebio.pin import put_input, pin
from utils.auth import login
from utils.widgets import toast_error_and_return, toast_warn_and_return, toast
from utils.callback import bind_enter_key_callback
from time import sleep


_login_finished: bool = False


def login_popup() -> None:
    popup(
        title="用户登录",
        content=[
            put_input("user_name", "text", label="用户名"),
            put_input("password", "password", label="密码"),
            put_button("登录", onclick=on_login_button_clicked, color="success")
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
