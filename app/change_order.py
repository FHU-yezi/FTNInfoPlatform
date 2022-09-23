from time import sleep
from typing import Dict

from bson import ObjectId
from pywebio.output import put_buttons, put_markdown, toast, use_scope
from pywebio.pin import pin, pin_on_change, pin_update, put_input
from utils.auth import check_cookie, get_uid_from_cookie, new_cookie
from utils.db import trade_data_db
from utils.page import (close_page, get_base_url, get_cookie, get_url_params,
                        jump_to, set_cookie)
from utils.popup import login_popup
from utils.widgets import toast_error_and_return, toast_warn_and_return

NAME: str = "修改意向单"
DESC: str = "修改交易意向"
VISIBILITY: bool = False
uid: str = ""  # TODO


def get_order_data(order_id: str) -> Dict:
    return trade_data_db.find_one({"_id": ObjectId(order_id)})


def on_price_or_amount_input_changed(_) -> None:
    price: float = pin.price
    amount: float = pin.amount

    if not price or not amount:
        return

    if not 0 < price <= 3 or not 0 < amount <= 10 ** 8:
        return

    total_price: float = round(price * amount, 2)
    pin_update("total_price", value=total_price)


def on_publish_button_clicked() -> None:
    global uid
    order_id: str = get_url_params()["order_id"]
    price: float = pin.price
    amount: int = pin.amount
    # TODO
    total_price: float = round(price * amount, 2)

    if not price or not amount:
        toast_warn_and_return("请输入价格和数量")

    if price <= 0 or amount <= 0:
        toast_error_and_return("价格和数量必须大于 0")

    # TODO
    order_data = get_order_data(order_id)
    order_data["order"] = {
        "type": order_data["order"]["type"],
        "price": price,
        "amount": amount,
        "total_price": total_price
    }

    trade_data_db.update_one(
        {"_id": ObjectId(order_id)},
        {"$set": order_data}
    )

    toast("交易单更新成功！", color="success")
    # 将按钮设为不可用
    # TODO
    with use_scope("buttons", clear=True):
        put_buttons(
            buttons=[
                {"label": "已更新", "value": "publish", "color": "success", "disabled": True},
                {"label": "取消", "value": "cancel"}
            ],
            onclick=[
                on_publish_button_clicked,
                on_cancel_button_clicked
            ]
        )
    sleep(1)
    jump_to(get_base_url() + "?app=my_orders")


def on_cancel_button_clicked() -> None:
    close_page()


def change_order() -> None:
    url_params = get_url_params()
    order_id: str = url_params.get("order_id")
    if not order_id:
        toast_error_and_return("请求参数错误")

    order_data = get_order_data(order_id)
    if not order_data:
        toast_error_and_return("请求参数错误")

    put_markdown("# 修改意向单")
    if not check_cookie(get_cookie()):
        login_popup()
        set_cookie(new_cookie(pin.user_name, pin.password))

    global uid
    uid = get_uid_from_cookie(get_cookie())
    if order_data["user"]["id"] != uid:
        toast_error_and_return("您无权修改该意向单")

    put_input("order_id", "text", label="意向单 ID",
              value=str(order_data["_id"]), readonly=True)
    put_input("publish_time", "text", label="发布时间",
              value=str(order_data["publish_time"]), readonly=True)
    put_input("order_type", "text", label="意向类型",
              value=("买" if order_data["order"]["type"] == "buy" else "卖"),
              readonly=True)
    put_input("price", "float", label="单价",
              value=order_data["order"]["price"])
    put_input("amount", "number", label="数量",
              value=order_data["order"]["amount"])
    put_input("total_price", "number", label="总价",
              value=order_data["order"]["total_price"], readonly=True)
    with use_scope("buttons", clear=True):
        put_buttons(
            buttons=[
                {"label": "更新", "value": "publish", "color": "success"},
                {"label": "取消", "value": "cancel"}
            ],
            onclick=[
                on_publish_button_clicked,
                on_cancel_button_clicked
            ]
        )

    pin_on_change("price", onchange=on_price_or_amount_input_changed)
    pin_on_change("amount", onchange=on_price_or_amount_input_changed)
