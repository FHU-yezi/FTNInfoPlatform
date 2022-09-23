from time import sleep
from typing import Literal

from pywebio.output import put_buttons, put_markdown, toast, use_scope
from pywebio.pin import pin, pin_on_change, pin_update, put_input, put_select
from utils.auth import check_cookie, get_uid_from_cookie, new_cookie
from utils.db import trade_data_db, user_data_db
from utils.page import (close_page, get_base_url, get_cookie, jump_to,
                        set_cookie)
from utils.popup import login_popup
from utils.time_helper import get_now_without_mileseconds
from utils.widgets import toast_error_and_return, toast_warn_and_return

NAME: str = "发布意向单"
DESC: str = "发布交易意向"
VISIBILITY: bool = True


def is_already_has_order(uid: str, order_type: str) -> bool:
    return trade_data_db.count_documents(
        {"user.id": uid, "order.type": order_type}
    ) != 0


def get_name_from_uid(uid: str) -> str:
    return user_data_db.find_one({"_id": uid})["user_name"]


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
    order_type: Literal["buy", "sell"] = "buy" if pin.order_type == "买单" else "sell"
    price: float = pin.price
    amount: int = pin.amount
    total_price: float = pin.total_price

    if not price or not amount:
        toast_warn_and_return("请输入价格和数量")

    if price <= 0 or amount <= 0:
        toast_error_and_return("价格和数量必须大于 0")

    if is_already_has_order(uid, order_type):
        toast_warn_and_return("您已经发布过该类型的交易单")

    trade_data_db.insert_one({
        "publish_time": get_now_without_mileseconds(),
        "order": {
            "type": order_type,
            "price": price,
            "amount": amount,
            "total_price": total_price
        },
        "user": {
            "id": uid,
            "name": get_name_from_uid(uid)
        }
    })

    toast("交易单发布成功！", color="success")
    # 将按钮设为不可用
    # TODO
    with use_scope("buttons", clear=True):
        put_buttons(
            buttons=[
                {"label": "已发布", "value": "publish", "color": "success", "disabled": True},
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


def publish_order() -> None:
    put_markdown("# 发布意向单")
    if not check_cookie(get_cookie()):
        login_popup()
        set_cookie(new_cookie(pin.user_name, pin.password))

    global uid
    uid = get_uid_from_cookie(get_cookie())

    put_select("order_type", label="意向类型", options=["买单", "卖单"],
               value="买单", help_text="我要买贝 => 买单，我要卖贝 => 卖单")
    put_input("price", "float", label="单价")
    put_input("amount", "number", label="数量")
    put_input("total_price", "float", label="总价", readonly=True)
    with use_scope("buttons", clear=True):
        put_buttons(
            buttons=[
                {"label": "发布", "value": "publish", "color": "success"},
                {"label": "取消", "value": "cancel"}
            ],
            onclick=[
                on_publish_button_clicked,
                on_cancel_button_clicked
            ]
        )

    pin_on_change("price", onchange=on_price_or_amount_input_changed)
    pin_on_change("amount", onchange=on_price_or_amount_input_changed)
