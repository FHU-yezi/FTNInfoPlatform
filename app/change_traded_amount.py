from pywebio.output import (
    clear_scope,
    put_buttons,
    put_markdown,
    put_success,
    use_scope,
)
from pywebio.pin import pin, pin_on_change, pin_update, put_input

from data.order_new import Order
from data.token_new import Token
from utils.callback import bind_enter_key_callback
from utils.exceptions import (
    AmountIlliegalError,
    OrderIDNotExistError,
    TokenNotExistError,
)
from utils.login import require_login
from utils.page import (
    close_page,
    get_token,
    get_url_params,
    get_url_to_module,
    jump_to,
    set_token,
)
from widgets.toast import toast_error_and_return, toast_success

NAME: str = "修改已交易数量"
DESC: str = "修改意向单的已交易数量"
VISIBILITY: bool = False


def on_traded_amount_input_changed() -> None:
    traded_amount: int = pin.traded_amount
    total_amount: int = pin.total_amount

    if traded_amount is None:
        return

    if not 0 < traded_amount <= total_amount:
        return

    remaining_amount: int = total_amount - traded_amount
    if remaining_amount == 0:
        with use_scope("finish_info", clear=True):
            put_success("在您点击提交按钮后，该交易单将被自动标记为完成，并从您的意向单列表中消失")
    else:
        clear_scope("finish_info")
    pin_update("remaining_amount", value=remaining_amount)


def on_change_button_clicked(order: Order) -> None:
    new_traded_amount: int = pin.traded_amount

    try:
        order.change_traded_amount(new_traded_amount)
    except AmountIlliegalError:
        toast_error_and_return("已交易数量为空或不在正常范围内")
    else:
        toast_success("更新成功")
        # 将按钮设为不可用
        # TODO
        with use_scope("buttons", clear=True):
            put_buttons(
                buttons=[
                    {
                        "label": "已更新",
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
        jump_to(get_url_to_module("my_orders"))


def change_traded_amount() -> None:
    order_id = get_url_params().get("order_id")
    if not order_id:
        toast_error_and_return("请求参数错误")

    try:
        order = Order.from_id(order_id)
    except OrderIDNotExistError:
        toast_error_and_return("请求参数错误")

    try:
        user = Token.from_token_value(get_token()).user
    except TokenNotExistError:
        user = require_login()
        token = user.generate_token()
        set_token(token.value)

    if order.user != user:
        toast_error_and_return("您无权修改该意向单")

    put_markdown("# 修改已交易数量")
    put_markdown(
        f"""
        发布时间：{order.publish_time}
        意向单类型：{"买单" if order.type == "buy" else "卖单"}
        """
    )
    put_input(
        "unit_price",
        "float",
        label="单价",
        value=order.unit_price,
        readonly=True,
    )
    put_input(
        "total_amount",
        "number",
        label="总量",
        value=order.total_amount,
        readonly=True,
    )
    put_input(
        "traded_amount",
        "number",
        label="已交易",
        value=order.traded_amount,
        help_text="不能小于当前值，不能大于总量",
    )
    put_input(
        "remaining_amount",
        "number",
        label="剩余",
        value=order.remaining_amount,
        readonly=True,
    )
    put_input(
        "total_price",
        "number",
        label="总价",
        value=order.total_price,
        readonly=True,
    )
    with use_scope("buttons", clear=True):
        put_buttons(
            buttons=[
                {
                    "label": "更新",
                    "value": "publish",
                    "color": "success",
                },
                {
                    "label": "取消",
                    "value": "cancel",
                },
            ],
            onclick=[
                lambda: on_change_button_clicked(order),
                close_page,
            ],
        )
    with use_scope("finish_info", clear=True):
        pass  # 交易单将被结束的提示区域

    pin_on_change(
        "traded_amount",
        onchange=lambda _: on_traded_amount_input_changed(),
    )
    bind_enter_key_callback(
        "traded_amount",
        on_press=lambda _: on_change_button_clicked(order),
    )
