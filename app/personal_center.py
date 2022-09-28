from pywebio.output import (
    close_popup,
    popup,
    put_button,
    put_buttons,
    put_markdown,
    put_row,
    use_scope,
)
from pywebio.pin import pin, put_input
from utils.callback import bind_enter_key_callback
from utils.config import config
from utils.data.token import create_token, expire_token, verify_token
from utils.data.user import (
    change_password,
    change_user_name,
    get_user_data_from_uid,
)
from utils.exceptions import (
    DuplicatedUsernameError,
    PasswordIlliegalError,
    PasswordNotChangedError,
    PasswordNotEqualError,
    TokenNotExistError,
    UsernameIlliegalError,
    UsernameNotChangedError,
    UsernameOrPasswordWrongError,
    WeakPasswordError,
)
from utils.login import require_login
from utils.page import get_token, reload, set_token
from utils.widgets import (
    toast_error_and_return,
    toast_success,
    toast_warn_and_return,
)

NAME: str = "个人中心"
DESC: str = "查看并修改自己的个人信息"
VISIBILITY: bool = True


def on_change_user_name_button_clicked(uid: str, old_user_name: str) -> None:
    with popup(title="修改昵称", size="large"):
        put_input(
            "new_user_name",
            "text",
            label="新昵称",
            help_text="建议与您的简书昵称相同",
            value=old_user_name,
        )

        with use_scope("buttons", clear=True):
            put_buttons(
                [
                    {
                        "label": "确定",
                        "value": "confirm",
                        "color": "success",
                    },
                    {
                        "label": "取消",
                        "value": "cancel",
                    },
                ],
                onclick=[
                    lambda: on_change_user_name_confirmed(uid),
                    close_popup,
                ],
            )
            bind_enter_key_callback(
                "new_user_name",
                on_press=lambda _: on_change_user_name_confirmed(uid),
            )


def on_change_user_name_confirmed(uid: str) -> None:
    new_user_name: str = pin.new_user_name

    try:
        change_user_name(uid, new_user_name)
    except UsernameIlliegalError:
        toast_error_and_return("新昵称为空或不合法")
    except DuplicatedUsernameError:
        toast_warn_and_return("新昵称已被占用")
    except UsernameNotChangedError:
        toast_warn_and_return("新昵称不能与旧昵称相同")
    else:
        toast_success("修改成功")
        # 将按钮设为不可用
        # TODO
        with use_scope("buttons", clear=True):
            put_buttons(
                [
                    {
                        "label": "确定",
                        "value": "confirm",
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
        reload(delay=1)


def on_change_password_button_clicked(uid: str) -> None:
    with popup("修改密码", size="large"):
        put_input(
            "old_password",
            "password",
            label="旧密码",
        ),
        put_input(
            "new_password",
            "password",
            label="新密码",
        ),
        put_input(
            "new_password_again",
            "password",
            label="确认密码",
            help_text="长度至少为 8 位，至少包含 1 个字母和 1 个数字",
        ),
        with use_scope("buttons", clear=True):
            put_buttons(
                [
                    {
                        "label": "确定",
                        "value": "confirm",
                        "color": "success",
                    },
                    {
                        "label": "取消",
                        "value": "cancel",
                    },
                ],
                onclick=[
                    lambda: on_change_password_confirmed(uid),
                    close_popup,
                ],
            )
    bind_enter_key_callback(
        "new_password_again",
        on_press=lambda _: on_change_password_confirmed(uid),
    )


def on_change_password_confirmed(uid: str) -> None:
    old_password: str = pin.old_password
    new_password: str = pin.new_password
    new_password_again: str = pin.new_password_again

    try:
        change_password(uid, old_password, new_password, new_password_again)
    except PasswordIlliegalError:
        toast_error_and_return("密码为空或不合法")
    except WeakPasswordError:
        toast_warn_and_return("新密码强度不足")
    except PasswordNotEqualError:
        toast_warn_and_return("两次输入的密码不一致")
    except UsernameOrPasswordWrongError:
        toast_error_and_return("旧密码错误")
    except PasswordNotChangedError:
        toast_warn_and_return("新密码不能与旧密码相同")
    else:
        expire_token(get_token())
        toast_success("修改成功，您将需要重新登录")
        # 将按钮设为不可用
        # TODO
        with use_scope("buttons", clear=True):
            put_buttons(
                [
                    {
                        "label": "确定",
                        "value": "confirm",
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
        reload(delay=1)


def on_change_token_expire_time_button_clicked(
    uid: str, now_token_expire_hour: int
) -> None:
    # TODO
    pass


def on_change_token_expire_time_confirmed() -> None:
    # TODO
    pass


def on_logout_button_clicked() -> None:
    expire_token(get_token())
    toast_success("您已安全退出")
    reload(delay=1)


def personal_center() -> None:
    try:
        uid = verify_token(get_token())
    except TokenNotExistError:
        uid = require_login()
        set_token(create_token(uid))

    user_data = get_user_data_from_uid(uid)

    put_markdown("# 个人中心")

    put_markdown("## 基本信息")
    old_user_name: str = user_data["user_name"]
    put_row(
        [
            put_markdown(f"昵称：{user_data['user_name']}"),
            put_button(
                "修改",
                onclick=lambda: on_change_user_name_button_clicked(uid, old_user_name),
                color="success",
                small=True,
            ),
        ],
        size="1fr auto",
    )
    put_markdown(
        f"""
        UID：{uid}
        注册时间：{user_data['signup_time']}
        """
    )
    put_button(
        "修改密码",
        onclick=lambda: on_change_password_button_clicked(uid),
        color="success",
        small=True,
    )

    now_token_expire_hour: int = user_data.get(
        "customize_token_expire_hours", config.token_expire_hours
    )
    put_markdown(
        f"""
        ## 鉴权有效期

        该设置影响您被要求重新登录的频率。

        将该值调大可以减少被要求登录的次数，但会略微降低账户安全性。

        默认值为 {config.token_expire_hours} 小时。
        """
    )
    put_row(
        [
            put_markdown(f"当前值：{now_token_expire_hour} 小时"),
            put_button(
                "修改（该功能正在开发中）",
                onclick=lambda: on_change_token_expire_time_button_clicked(
                    uid, now_token_expire_hour
                ),
                color="success",
                small=True,
                outline=True,
                disabled=True,
            ),
            None,
        ],
        size="120px auto auto",
    )

    put_markdown(
        """
        # 退出登录

        安全退出系统。
        """
    )
    put_button(
        "退出登录",
        onclick=on_logout_button_clicked,
        color="warning",
    )
