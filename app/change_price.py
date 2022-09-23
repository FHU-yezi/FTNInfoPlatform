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

NAME: str = "修改价格"
DESC: str = "修改意向单的价格"
VISIBILITY: bool = False
uid: str = ""  # TODO


def get_order_data(order_id: str) -> Dict:
    return trade_data_db.find_one({"_id": ObjectId(order_id)})


def on_price_or_amount_input_changed(_) -> None:
    price: float = pin.price
    total_amount: float = pin.total_amount

    if not price or not total_amount:
        return

    if not 0 < price <= 3 or not 0 < total_amount <= 10 ** 8:
        return

    total_price: float = round(price * total_amount, 2)
    pin_update("total_price", value=total_price)


def on_change_button_clicked() -> None:
    global uid
    order_id: str = get_url_params()["order_id"]
    price: float = pin.price
    total_amount: int = pin.total_amount
    traded_amount: int = pin.traded_amount
    remaining_amount: int = pin.remaining_amount
    # TODO
    total_price: float = round(price * total_amount, 2)

    if not price:
        toast_warn_and_return("请输入价格")

    if price <= 0:
        toast_error_and_return("价格必须大于 0")

    # TODO
    order_data = get_order_data(order_id)
    order_data["order"] = {
        "type": order_data["order"]["type"],
        "price": {
            "single": price,
            "total": total_price
        },
        "amount": {
            "total": total_amount,
            "traded": 0,
            "remaining": total_amount
        }
    }

    trade_data_db.update_one(
        {"_id": ObjectId(order_id)},
        {"$set": order_data}
    )

    toast("更新成功", color="success")
    # 将按钮设为不可用
    # TODO
    with use_scope("buttons", clear=True):
        put_buttons(
            buttons=[
                {"label": "已更新", "value": "publish", "color": "success", "disabled": True},
                {"label": "取消", "value": "cancel"}
            ],
            onclick=[
                on_change_button_clicked,
                on_cancel_button_clicked
            ]
        )
    sleep(1)
    jump_to(get_base_url() + "?app=my_orders")


def on_cancel_button_clicked() -> None:
    close_page()


def change_price() -> None:
    url_params = get_url_params()
    order_id: str = url_params.get("order_id")
    if not order_id:
        toast_error_and_return("请求参数错误")

    order_data = get_order_data(order_id)
    if not order_data:
        toast_error_and_return("请求参数错误")

    put_markdown("# 修改意向单价格")
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
              value=order_data["order"]["price"]["single"])
    put_input("total_amount", "number", label="总量",
              value=order_data["order"]["amount"]["total"], readonly=True)
    put_input("traded_amount", "number", label="已交易",
              value=order_data["order"]["amount"]["traded"], readonly=True)
    put_input("remaining_amount", "number", label="剩余",
              value=order_data["order"]["amount"]["remaining"], readonly=True)
    put_input("total_price", "number", label="总价",
              value=order_data["order"]["price"]["total"], readonly=True)
    with use_scope("buttons", clear=True):
        put_buttons(
            buttons=[
                {"label": "更新", "value": "publish", "color": "success"},
                {"label": "取消", "value": "cancel"}
            ],
            onclick=[
                on_change_button_clicked,
                on_cancel_button_clicked
            ]
        )

    pin_on_change("price", onchange=on_price_or_amount_input_changed)
    pin_on_change("total_amount", onchange=on_price_or_amount_input_changed)
