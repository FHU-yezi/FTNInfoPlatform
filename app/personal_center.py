from data.token import create_token, expire_token, verify_token
from data.user import (
    bind_jianshu_account,
    change_password,
    change_user_name,
    get_user_data_from_uid,
)
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
from utils.exceptions import (
    DuplicatedUsernameError,
    DuplicatedUserURLError,
    PasswordIlliegalError,
    PasswordNotChangedError,
    PasswordNotEqualError,
    TokenNotExistError,
    UsernameIlliegalError,
    UsernameNotChangedError,
    UsernameOrPasswordWrongError,
    UserURLIlliegalError,
    WeakPasswordError,
)
from utils.login import require_login
from utils.page import get_token, reload, set_token
from widgets.toast import (
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


def on_logout_button_clicked() -> None:
    expire_token(get_token())
    toast_success("您已安全退出")
    reload(delay=1)


def on_bind_jianshu_account_button_clicked(uid: str):
    with popup("绑定简书账号", size="large"):
        put_markdown(
            """
            绑定简书账号后，其它用户可在意向单列表中一键跳转至您的简书主页，交易更加方便。
            """
        ),
        put_input(
            "jianshu_url",
            "text",
            label="简书用户主页 URL",
            help_text="示例：https://www.jianshu.com/u/ea36c8d8aa30",
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
                    lambda: on_bind_jianshu_account_confirmed(uid),
                    close_popup,
                ],
            )
    bind_enter_key_callback(
        "jianshu_url",
        on_press=lambda _: on_bind_jianshu_account_confirmed(uid),
    )


def on_bind_jianshu_account_confirmed(uid: str):
    jianshu_url: str = pin.jianshu_url
    try:
        jianshu_name: str = bind_jianshu_account(uid, jianshu_url)
    except UserURLIlliegalError:
        toast_error_and_return("链接为空或输入错误")
    except DuplicatedUserURLError:
        toast_warn_and_return("该简书账号已被他人绑定")
    else:
        toast_success(f"您已成功绑定简书账号 {jianshu_name}")
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
            None,
            put_button(
                "修改",
                onclick=lambda: on_change_user_name_button_clicked(uid, old_user_name),
                color="success",
                small=True,
            ),
        ],
        size="auto 10px 1fr",
    )
    put_row(
        [
            put_markdown(
                "简书账号："
                + (
                    f"已绑定（{user_data['jianshu']['name']}）"
                    if user_data["jianshu"]["url"]
                    else "未绑定"
                )
            ),
            None,
            put_button(
                "绑定简书账号",
                onclick=lambda: on_bind_jianshu_account_button_clicked(uid),
                color="success",
                small=True,
            )
            if not user_data["jianshu"]["url"]
            else put_markdown(""),
        ],
        size="auto 10px 1fr",
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

    put_markdown(
        """
        ## 退出登录

        安全退出系统。
        """
    )
    put_button(
        "退出登录",
        onclick=on_logout_button_clicked,
        color="warning",
    )
