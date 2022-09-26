from time import sleep
from typing import Dict

from bson import ObjectId
from pywebio.output import put_buttons, put_markdown, use_scope
from pywebio.pin import pin, pin_on_change, pin_update, put_input
from utils.data.order import (
    change_order_traded_amount,
    get_order_data_from_order_id,
)
from utils.data.token import create_token, verify_token
from utils.db import order_data_db
from utils.exceptions import (
    AmountIlliegalError,
    OrderIDNotExistError,
    TokenNotExistError,
)
from utils.page import (
    close_page,
    get_token,
    get_url_params,
    get_url_to_module,
    jump_to,
    set_token,
)
from utils.login import require_login
from utils.widgets import toast_error_and_return, toast_success

NAME: str = "修改已交易数量"
DESC: str = "修改意向单的已交易数量"
VISIBILITY: bool = False


def get_order_data(order_id: str) -> Dict:
    return order_data_db.find_one({"_id": ObjectId(order_id)})


def on_traded_amount_input_changed(_) -> None:
    traded_amount: int = pin.traded_amount
    total_amount: int = pin.total_amount

    if traded_amount is None:
        return

    if not 0 < traded_amount <= total_amount:
        return

    remaining_amount: int = total_amount - traded_amount
    pin_update("remaining_amount", value=remaining_amount)


def on_change_button_clicked(order_id: str) -> None:
    traded_amount: int = pin.traded_amount

    try:
        change_order_traded_amount(order_id, traded_amount)
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
                    on_change_button_clicked,
                    on_cancel_button_clicked,
                ],
            )
        sleep(1)
        jump_to(get_url_to_module("my_orders"))


def on_cancel_button_clicked() -> None:
    close_page()


def change_traded_amount() -> None:
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

    put_markdown("# 修改已交易数量")
    put_input(
        "publish_time",
        "text",
        label="发布时间",
        value=str(order_data["publish_time"]),
        readonly=True,
    )
    put_input(
        "order_type",
        "text",
        label="意向类型",
        value=("买" if order_data["order"]["type"] == "buy" else "卖"),
        readonly=True,
    )
    put_input(
        "unit_price",
        "float",
        label="单价",
        value=order_data["order"]["price"]["unit"],
        readonly=True,
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
    )
    put_input(
        "remaining_amount",
        "number",
        label="剩余",
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
                {"label": "更新", "value": "publish", "color": "success"},
                {"label": "取消", "value": "cancel"},
            ],
            onclick=[
                lambda: on_change_button_clicked(order_id),
                on_cancel_button_clicked,
            ],
        )

    pin_on_change(
        "traded_amount",
        onchange=lambda _: on_traded_amount_input_changed(order_id),
    )
