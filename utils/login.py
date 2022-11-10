from queue import Queue

from pywebio.output import close_popup, popup, put_buttons
from pywebio.pin import pin, put_input

from data.user import User
from utils.callback import bind_enter_key_callback
from utils.exceptions import (
    PasswordIlliegalError,
    UsernameIlliegalError,
    UsernameOrPasswordWrongError,
)
from utils.page import get_url_to_module, jump_to
from widgets.toast import (
    toast_error_and_return,
    toast_success,
    toast_warn_and_return,
)


def require_login() -> User:
    uid_container: Queue = Queue(1)

    with popup("登录", size="large", closable=False):
        put_input(
            "user_name",
            "text",
            label="用户名",
        ),
        put_input(
            "password",
            "password",
            label="密码",
        ),
        put_buttons(
            buttons=[
                {
                    "label": "登录",
                    "value": "login",
                    "color": "success",
                },
                {
                    "label": "注册",
                    "value": "signup",
                },
            ],
            onclick=[
                lambda: on_login_button_clicked(uid_container),
                on_signup_button_clicked,
            ],
        ),
    bind_enter_key_callback(
        "password",
        lambda _: on_login_button_clicked(uid_container),
    )

    # 阻塞等待结果
    uid = uid_container.get()
    return User.from_id(uid)


def on_login_button_clicked(uid_container: Queue) -> None:
    user_name: str = pin.user_name
    password: str = pin.password

    try:
        uid = User.login(user_name, password)
    except UsernameIlliegalError:
        toast_warn_and_return("请输入用户名")
    except PasswordIlliegalError:
        toast_warn_and_return("请输入密码")
    except UsernameOrPasswordWrongError:
        toast_error_and_return("用户名或密码错误")
    else:
        toast_success("登录成功")
        close_popup()
        uid_container.put(uid)


def on_signup_button_clicked() -> None:
    jump_to(get_url_to_module("signup"))
