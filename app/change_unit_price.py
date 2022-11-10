from pywebio.output import put_buttons, put_markdown, use_scope
from pywebio.pin import pin, pin_on_change, pin_update, put_input

from data.order_new import Order
from data.overview import get_24h_traded_FTN_avg_price
from data.token_new import Token
from utils.callback import bind_enter_key_callback
from utils.exceptions import (
    OrderIDNotExistError,
    PriceIlliegalError,
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

NAME: str = "修改单价"
DESC: str = "修改意向单的单价"
VISIBILITY: bool = False


def on_unit_price_input_changed(_) -> None:
    unit_price: float = pin.unit_price
    total_amount: float = pin.total_amount

    if not unit_price:
        return

    if not 0.05 < unit_price <= 0.2:
        return

    total_price: float = round(unit_price * total_amount, 2)
    pin_update("total_price", value=total_price)


def on_change_button_clicked(order: Order) -> None:
    new_unit_price: float = pin.unit_price

    try:
        order.change_unit_price(new_unit_price)
    except PriceIlliegalError:
        toast_error_and_return("单价为空或不在正常范围内")
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
        jump_to(get_url_to_module("my_orders"), delay=1)


def change_unit_price() -> None:
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

    put_markdown("# 修改意向单价格")
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
        help_text=f"市场参考价：{get_24h_traded_FTN_avg_price(order.type, missing='default')}",
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
        readonly=True,
    )
    put_input(
        "remaining_amount",
        "number",
        label="剩余可交易",
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

    pin_on_change(
        "unit_price",
        onchange=on_unit_price_input_changed,
    )
    bind_enter_key_callback(
        "unit_price",
        on_press=lambda _: on_change_button_clicked(order),
    )
