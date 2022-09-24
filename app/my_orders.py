from time import sleep

from pywebio.output import close_popup, popup, put_buttons, put_markdown, toast
from utils.data.order import delete_order, get_my_active_order
from utils.data.token import create_token, verify_token
from utils.exceptions import TokenNotExistError
from utils.html import link
from utils.page import (get_token, get_url_to_module, jump_to, reload,
                        set_token, set_url_params)
from utils.popup import login_popup

NAME: str = "我的意向单"
DESC: str = "查看并修改自己的意向单"
VISIBILITY: bool = True


def on_delete_confirmed(order_id: str):
    delete_order(order_id)
    toast("删除成功", color="success")
    sleep(1)
    reload()


def on_change_unit_price_button_clicked(order_id: str):
    jump_to(set_url_params(
        get_url_to_module("change_unit_price"),
        {"order_id": order_id}
    ))


def on_change_traded_amount_button_clicked(order_id: str):
    jump_to(set_url_params(
        get_url_to_module("change_traded_amount"),
        {"order_id": order_id}
    ))


def on_order_delete_button_clicked(order_id: str):
    with popup("确认删除"):
        put_markdown("确认要删除这条意向单吗？")
        put_buttons(
            buttons=[
                {"label": "确认", "value": "confirm", "color": "warning"},
                {"label": "取消", "value": "cancel"}
            ],
            onclick=[
                lambda: on_delete_confirmed(order_id),
                close_popup
            ]
        )


def my_orders() -> None:
    try:
        uid = verify_token(get_token())
    except TokenNotExistError:
        uid = login_popup()
        set_token(create_token(uid))

    put_markdown("# 我的意向单")

    buy_order_data = get_my_active_order(uid, "buy")
    if not buy_order_data:
        put_markdown(f"""
        ## 买单

        您目前没有买单，{link("去发布>>>", get_url_to_module("publish_order"), new_window=True)}
        """, sanitize=False)
    else:
        buy_order_id = str(buy_order_data["_id"])
        put_markdown(f"""
        ## 买单

        发布时间：{buy_order_data['publish_time']}
        单价：{buy_order_data['order']['price']['unit']}
        总量：{buy_order_data['order']['amount']['total']}
        已交易：{buy_order_data['order']['amount']['traded']}
        剩余：{buy_order_data['order']['amount']['remaining']}
        总价：{buy_order_data['order']['price']['total']}
        """, sanitize=False)
        put_buttons(
            buttons=[
                {"label": "修改单价", "value": "change_unit_price", "color": "success"},
                {"label": "修改已交易数量", "value": "change_traded_amount", "color": "success"},
                {"label": "删除", "value": "delete", "color": "warning"}
            ],
            onclick=[
                lambda: on_change_unit_price_button_clicked(buy_order_id),
                lambda: on_change_traded_amount_button_clicked(buy_order_id),
                lambda: on_order_delete_button_clicked(buy_order_id)
            ]
        )

    sell_order_data = get_my_active_order(uid, "sell")
    if not sell_order_data:
        put_markdown(f"""
        ## 卖单

        您目前没有卖单，{link("去发布>>>", get_url_to_module("publish_order"), new_window=True)}
        """, sanitize=False)
    else:
        sell_order_id = str(sell_order_data["_id"])
        put_markdown(f"""
        ## 卖单

        发布时间：{sell_order_data['publish_time']}
        单价：{sell_order_data['order']['price']['unit']}
        总量：{sell_order_data['order']['amount']['total']}
        已交易：{sell_order_data['order']['amount']['traded']}
        剩余：{sell_order_data['order']['amount']['remaining']}
        总价：{sell_order_data['order']['price']['total']}
        """, sanitize=False)
        put_buttons(
            buttons=[
                {"label": "修改价格", "value": "change_unit_price", "color": "success"},
                {"label": "修改已交易数量", "value": "change_traded_amount", "color": "success"},
                {"label": "删除", "value": "delete", "color": "warning"}
            ],
            onclick=[
                lambda: on_change_unit_price_button_clicked(sell_order_id),
                lambda: on_change_traded_amount_button_clicked(sell_order_id),
                lambda: on_order_delete_button_clicked(sell_order_id)
            ]
        )
