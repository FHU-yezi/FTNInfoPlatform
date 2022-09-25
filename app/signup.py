from time import sleep

from pywebio.output import put_buttons, put_markdown, use_scope
from pywebio.pin import pin, put_input
from utils.data.user import sign_up
from utils.exceptions import (
    DuplicatedUsernameError,
    PasswordIlliegalError,
    PasswordNotEqualError,
    UsernameIlliegalError,
    WeakPasswordError,
)
from utils.page import get_base_url, jump_to
from utils.page import set_token
from utils.data.token import create_token
from utils.widgets import (
    toast_error_and_return,
    toast_success,
    toast_warn_and_return,
)

NAME: str = "用户注册"
DESC: str = "注册新用户"
VISIBILITY: bool = False


def on_signup_button_clicked() -> None:
    user_name: str = pin.user_name
    passowrd: str = pin.password
    passowrd_again: str = pin.password_again

    try:
        uid: str = sign_up(
            user_name,
            passowrd,
            passowrd_again,
            admin_permissions_level=0,
            user_permissions_level=1,
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
                    {"label": "取消", "value": "cancel"},
                ],
                onclick=[on_signup_button_clicked, on_cancel_button_clicked],
            )
        # 为新注册的用户生成 Token
        # 免去用户登录流程
        set_token(create_token(uid))
        sleep(1)
        jump_to(get_base_url())


def on_cancel_button_clicked() -> None:
    jump_to(get_base_url())


def signup() -> None:
    put_markdown("# 注册")

    put_input("user_name", "text", label="用户名")
    put_input(
        "password", "password", label="密码", help_text="长度至少为 8 位，至少包含 1 个字母和 1 个数字"
    )
    put_input("password_again", "password", label="确认密码")

    with use_scope("buttons", clear=True):
        put_buttons(
            buttons=[
                {"label": "注册", "value": "publish", "color": "success"},
                {"label": "取消", "value": "cancel"},
            ],
            onclick=[on_signup_button_clicked, on_cancel_button_clicked],
        )
