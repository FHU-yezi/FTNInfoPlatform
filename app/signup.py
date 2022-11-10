from pywebio.output import put_buttons, put_markdown, use_scope
from pywebio.pin import pin, put_input

from data.user_new import User
from utils.callback import bind_enter_key_callback
from utils.exceptions import (
    DuplicatedUsernameError,
    PasswordIlliegalError,
    PasswordNotEqualError,
    UsernameIlliegalError,
    WeakPasswordError,
)
from utils.page import get_base_url, jump_to, set_token
from widgets.toast import (
    toast_error_and_return,
    toast_success,
    toast_warn_and_return,
)

NAME: str = "用户注册"
DESC: str = "注册新用户"
VISIBILITY: bool = False


def on_signup_button_clicked() -> None:
    user_name: str = pin.user_name
    password: str = pin.password
    password_again: str = pin.password_again

    try:
        user = User.signup(
            user_name,
            password,
            password_again,
            admin_permission_level=0,
            user_permission_level=1,
        )
    except UsernameIlliegalError:
        toast_error_and_return("用户名为空或不合法")
    except PasswordIlliegalError:
        toast_error_and_return("密码为空或不合法")
    except PasswordNotEqualError:
        toast_warn_and_return("两次输入的密码不一致")
    except WeakPasswordError:
        toast_error_and_return("密码强度不足")
    except DuplicatedUsernameError:
        toast_warn_and_return("该用户名已被占用")
    else:
        toast_success("注册成功")
        # 将按钮设为不可用
        # TODO
        with use_scope("buttons", clear=True):
            put_buttons(
                buttons=[
                    {
                        "label": "注册成功",
                        "value": "publish",
                        "color": "success",
                        "disabled": True,
                    },
                    {
                        "label": "取消",
                        "value": "cancel",
                    },
                ],
                onclick=[
                    lambda: None,
                    lambda: None,
                ],
            )
        # 为新注册的用户生成 Token，免去用户登录流程
        set_token(user.generate_token().value)
        jump_to(get_base_url(), delay=1)


def signup() -> None:
    put_markdown("# 注册")

    put_input(
        "user_name",
        "text",
        label="用户名",
        help_text="建议与您的简书昵称相同",
    )
    put_input(
        "password",
        "password",
        label="密码",
        help_text="长度至少为 8 位，至少包含 1 个字母和 1 个数字",
    )
    put_input(
        "password_again",
        "password",
        label="确认密码",
    )

    with use_scope("buttons", clear=True):
        put_buttons(
            buttons=[
                {
                    "label": "注册",
                    "value": "signup",
                    "color": "success",
                },
                {
                    "label": "取消",
                    "value": "cancel",
                },
            ],
            onclick=[
                on_signup_button_clicked,
                lambda: jump_to(get_base_url()),
            ],
        )

    bind_enter_key_callback(
        "password_again",
        on_press=lambda _: on_signup_button_clicked(),
    )
