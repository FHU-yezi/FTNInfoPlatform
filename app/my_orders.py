from time import sleep
from typing import Dict

from bson import ObjectId
from pywebio.output import close_popup, popup, put_buttons, put_markdown, toast
from pywebio.pin import pin
from utils.auth import check_cookie, get_uid_from_cookie, new_cookie
from utils.db import trade_data_db
from utils.html import link
from utils.page import get_base_url, get_cookie, jump_to, reload, set_cookie
from utils.popup import login_popup

NAME: str = "我的意向单"
DESC: str = "查看并修改自己的意向单"
VISIBILITY: bool = True
uid: str = ""


def on_buy_delete_confirmed():
    delete_order(get_order_data(uid, "buy")["_id"])
    toast("删除成功", color="success")
    sleep(1)
    reload()


def on_sell_delete_confirmed():
    delete_order(get_order_data(uid, "sell")["_id"])
    toast("删除成功", color="success")
    sleep(1)
    reload()


# TODO
def on_buy_order_change_button_clicked():
    jump_to(get_base_url() + "?app=change_order"
            f"&order_id={str(get_order_data(uid, 'buy')['_id'])}")


def on_sell_order_change_button_clicked():
    jump_to(get_base_url() + "?app=change_order"
            f"&order_id={str(get_order_data(uid, 'sell')['_id'])}")


def on_buy_order_delete_button_clicked():
    with popup("确认删除"):
        put_markdown("确认要删除这条意向单吗？")
        put_buttons(
            buttons=[
                {"label": "确认", "value": "confirm", "color": "warning"},
                {"label": "取消", "value": "cancel"}
            ],
            onclick=[
                on_buy_delete_confirmed,
                close_popup
            ]
        )


def on_sell_order_delete_button_clicked():
    with popup("确认删除"):
        put_markdown("确认要删除这条意向单吗？")
        put_buttons(
            buttons=[
                {"label": "确认", "value": "confirm", "color": "warning"},
                {"label": "取消", "value": "cancel"}
            ],
            onclick=[
                on_sell_delete_confirmed,
                close_popup
            ]
        )


def get_order_data(uid: str, order_type: str) -> Dict:
    return trade_data_db.find_one({"user.id": uid, "order.type": order_type})


def delete_order(order_id: str) -> None:
    trade_data_db.delete_one({"_id": ObjectId(order_id)})


def my_orders() -> None:
    put_markdown("# 我的意向单")
    if not check_cookie(get_cookie()):
        login_popup()
        set_cookie(new_cookie(pin.user_name, pin.password))

    global uid
    uid = get_uid_from_cookie(get_cookie())

    buy_order_data = get_order_data(uid, "buy")
    if not buy_order_data:
        put_markdown(f"""
        ## 买单

        您目前没有买单，{link("去发布>>>", get_base_url() + "?app=publish_order", new_window=True)}
        """, sanitize=False)
    else:
        put_markdown(f"""
        ## 买单

        发布时间：{buy_order_data['publish_time']}
        价格：{buy_order_data['order']['price']}
        数量：{buy_order_data['order']['amount']}
        总价：{buy_order_data['order']['total_price']}
        """, sanitize=False)
        put_buttons(
            buttons=[
                {"label": "修改", "value": "publish", "color": "success"},
                {"label": "删除", "value": "warning"}
            ],
            onclick=[
                on_buy_order_change_button_clicked,
                on_buy_order_delete_button_clicked
            ]
        )

    sell_order_data = get_order_data(uid, "sell")
    if not sell_order_data:
        put_markdown(f"""
        ## 卖单

        您目前没有卖单，{link("去发布>>>", get_base_url() + "?app=publish_order", new_window=True)}
        """, sanitize=False)
    else:
        put_markdown(f"""
        ## 卖单

        发布时间：{sell_order_data['publish_time']}
        价格：{sell_order_data['order']['price']}
        数量：{sell_order_data['order']['amount']}
        总价：{sell_order_data['order']['total_price']}
        """, sanitize=False)
        put_buttons(
            buttons=[
                {"label": "修改", "value": "publish", "color": "success"},
                {"label": "删除", "value": "warning"}
            ],
            onclick=[
                on_sell_order_change_button_clicked,
                on_sell_order_delete_button_clicked
            ]
        )
