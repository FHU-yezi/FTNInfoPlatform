from typing import Dict

from bson import ObjectId
from data.order import change_order_unit_price, get_order_data_from_order_id
from data.overview import get_24h_traded_FTN_avg_price
from data.token import create_token, verify_token
from pywebio.output import put_buttons, put_markdown, use_scope
from pywebio.pin import pin, pin_on_change, pin_update, put_input
from utils.callback import bind_enter_key_callback
from utils.db import order_data_db
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


def get_order_data(order_id: str) -> Dict:
    return order_data_db.find_one({"_id": ObjectId(order_id)})


def on_unit_price_input_changed(_) -> None:
    unit_price: float = pin.unit_price
    total_amount: float = pin.total_amount

    if not unit_price:
        return

    if not 0.05 < unit_price <= 0.2:
        return

    total_price: float = round(unit_price * total_amount, 2)
    pin_update("total_price", value=total_price)


def on_change_button_clicked(order_id: str) -> None:
    unit_price: float = pin.unit_price

    try:
        change_order_unit_price(order_id, unit_price)
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
        order_data = get_order_data_from_order_id(order_id)
    except OrderIDNotExistError:
        toast_error_and_return("请求参数错误")

    try:
        uid = verify_token(get_token())
    except TokenNotExistError:
        uid = require_login()
        set_token(create_token(uid))

    if order_data["user"]["id"] != uid:
        toast_error_and_return("您无权修改该意向单")

    put_markdown("# 修改意向单价格")
    order_type = order_data["order"]["type"]
    put_markdown(
        f"""
        发布时间：{order_data['publish_time']}
        意向单类型：{"买单" if order_data["order"]["type"] == "buy" else "卖单"}
        """
    )
    put_input(
        "unit_price",
        "float",
        label="单价",
        value=order_data["order"]["price"]["unit"],
        help_text=f"市场参考价：{get_24h_traded_FTN_avg_price(order_type, missing='default')}",
    )
    put_input(
        "total_amount",
        "number",
        label="总量",
        value=order_data["order"]["amount"]["total"],
        readonly=True,
    )
    put_input(
        "traded_amount",
        "number",
        label="已交易",
        value=order_data["order"]["amount"]["traded"],
        readonly=True,
    )
    put_input(
        "remaining_amount",
        "number",
        label="剩余可交易",
        value=order_data["order"]["amount"]["remaining"],
        readonly=True,
    )
    put_input(
        "total_price",
        "number",
        label="总价",
        value=order_data["order"]["price"]["total"],
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
                lambda: on_change_button_clicked(order_id),
                close_page,
            ],
        )

    pin_on_change(
        "unit_price",
        onchange=on_unit_price_input_changed,
    )
    bind_enter_key_callback(
        "unit_price",
        on_press=lambda _: on_change_button_clicked(order_id),
    )
