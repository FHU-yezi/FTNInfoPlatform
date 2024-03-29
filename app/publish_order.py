from typing import Literal

from pywebio.output import popup, put_buttons, put_markdown, use_scope
from pywebio.pin import pin, pin_on_change, pin_update, put_input, put_select

from data.order import Order
from data.overview import get_24h_traded_FTN_avg_price
from data.token import Token
from data.user import User
from utils.exceptions import (
    AmountIlliegalError,
    DuplicatedOrderError,
    PriceIlliegalError,
    TokenNotExistError,
)
from utils.html import link
from utils.login import require_login
from utils.page import (
    close_page,
    get_token,
    get_url_params,
    get_url_to_module,
    jump_to,
    set_token,
)
from widgets.toast import (
    toast_error_and_return,
    toast_success,
    toast_warn_and_return,
)

NAME: str = "发布意向单"
DESC: str = "发布交易意向"
VISIBILITY: bool = True


def on_unit_price_or_total_amount_input_changed(_) -> None:
    unit_price: float = pin.unit_price
    total_amount: float = pin.total_amount

    if not unit_price or not total_amount:
        return

    if not 0.05 < unit_price <= 0.2 or not 0 < total_amount <= 10**8:
        return

    total_price: float = round(unit_price * total_amount, 2)
    pin_update("total_price", value=total_price)


def on_order_type_changed(_) -> None:
    order_type: Literal["buy", "sell"] = "buy" if pin.order_type == "买单" else "sell"

    help_text: str = (
        f"市场参考价：{get_24h_traded_FTN_avg_price(order_type, missing='default')}"
    )
    pin_update("unit_price", help_text=help_text)


def on_publish_button_clicked(user: User) -> None:
    order_type: Literal["buy", "sell"] = "buy" if pin.order_type == "买单" else "sell"
    unit_price: float = pin.unit_price
    total_amount: int = pin.total_amount

    try:
        Order.create(order_type, unit_price, total_amount, user)
    except PriceIlliegalError:
        toast_error_and_return("单价为空或不在正常范围内")
    except AmountIlliegalError:
        toast_error_and_return("总量为空或不在正常范围内")
    except DuplicatedOrderError:
        # TODO: 允许用户删除之前的交易单，并重新发布新意向单
        toast_warn_and_return("您已经发布过该类型的意向单")
    else:
        toast_success("发布成功")
        # 将按钮设为不可用
        # TODO
        with use_scope("buttons", clear=True):
            put_buttons(
                buttons=[
                    {
                        "label": "已发布",
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


def publish_order() -> None:
    try:
        user = Token.from_token_value(get_token()).user
    except TokenNotExistError:
        user = require_login()
        token = user.generate_token()
        set_token(token.value)

    # 如果用户没有绑定简书账号，阻止其发布交易单
    if not user.is_jianshu_binded:
        with popup("绑定简书账号", size="large", closable=False):  # 不可关闭
            put_markdown(
                f"""
                为避免虚假挂单干扰平台秩序，请在发布意向单前绑定简书账号。

                {link("去绑定>>>", get_url_to_module("personal_center"), new_window=True)}
                """,
                sanitize=False,
            )

    order_type = "买单" if get_url_params().get("order_type", "buy") == "buy" else "卖单"

    put_markdown("# 发布意向单")
    put_select(
        "order_type",
        label="意向类型",
        options=["买单", "卖单"],
        value=order_type,
        help_text="我要买贝 => 买单，我要卖贝 => 卖单",
    )
    put_input(
        "unit_price",
        "float",
        label="单价",
        help_text=f"市场参考价：{get_24h_traded_FTN_avg_price('buy', missing='default')}",
    )  # 默认 order_type 为 buy
    put_input(
        "total_amount",
        "number",
        label="总量",
    )
    put_input(
        "total_price",
        "float",
        label="总价",
        readonly=True,
    )
    with use_scope("buttons", clear=True):
        put_buttons(
            buttons=[
                {
                    "label": "发布",
                    "value": "publish",
                    "color": "success",
                },
                {
                    "label": "取消",
                    "value": "cancel",
                },
            ],
            onclick=[
                lambda: on_publish_button_clicked(user),
                close_page,
            ],
        )

    pin_on_change(
        "price",
        onchange=lambda _: on_unit_price_or_total_amount_input_changed(user),
    )
    pin_on_change(
        "total_amount",
        onchange=lambda _: on_unit_price_or_total_amount_input_changed(user),
    )
    pin_on_change(
        "order_type",
        onchange=on_order_type_changed,
    )
