from data.order import delete_order, get_my_active_order
from data.token import create_token, verify_token
from pywebio.output import (
    close_popup,
    popup,
    put_buttons,
    put_markdown,
    toast,
)
from utils.exceptions import TokenNotExistError
from utils.html import link
from utils.login import require_login
from utils.page import (
    get_token,
    get_url_to_module,
    jump_to,
    reload,
    set_token,
)
from widgets.order import put_order_detail

NAME: str = "我的意向单"
DESC: str = "查看并修改自己的意向单"
VISIBILITY: bool = True


def on_delete_confirmed(order_id: str):
    delete_order(order_id)
    toast("删除成功", color="success")
    reload(delay=1)


def on_change_unit_price_button_clicked(order_id: str):
    jump_to(
        get_url_to_module(
            "change_unit_price",
            {"order_id": order_id},
        ),
    )


def on_change_traded_amount_button_clicked(order_id: str):
    jump_to(
        get_url_to_module(
            "change_traded_amount",
            {"order_id": order_id},
        ),
    )


def on_order_delete_button_clicked(order_id: str):
    with popup("确认删除"):
        put_markdown("确认要删除这条意向单吗？")
        put_buttons(
            buttons=[
                {"label": "确认", "value": "confirm", "color": "warning"},
                {"label": "取消", "value": "cancel"},
            ],
            onclick=[
                lambda: on_delete_confirmed(order_id),
                close_popup,
            ],
        )


def my_orders() -> None:
    try:
        uid = verify_token(get_token())
    except TokenNotExistError:
        uid = require_login()
        set_token(create_token(uid))

    put_markdown("# 我的意向单")

    buy_order_data = get_my_active_order(uid, "buy")
    if not buy_order_data:
        put_markdown(
            f"""
            ## 买单

            您目前没有买单，{link("去发布>>>", get_url_to_module(
                "publish_order", params={"order_type": "buy"}
            ), new_window=True)}
            """,
            sanitize=False,
        )
    else:
        buy_order_id = str(buy_order_data["_id"])
        put_order_detail(
            order_id=buy_order_id,
            order_type=buy_order_data["order"]["type"],
            publish_time=buy_order_data["publish_time"],
            unit_price=buy_order_data["order"]["price"]["unit"],
            total_price=buy_order_data["order"]["price"]["total"],
            total_amount=buy_order_data["order"]["amount"]["total"],
            traded_amount=buy_order_data["order"]["amount"]["traded"],
            remaining_amount=buy_order_data["order"]["amount"]["remaining"],
        )
        put_buttons(
            buttons=[
                {
                    "label": "修改单价",
                    "value": "change_unit_price",
                    "color": "success",
                },
                {
                    "label": "修改已交易数量",
                    "value": "change_traded_amount",
                    "color": "success",
                },
                {
                    "label": "删除",
                    "value": "delete",
                    "color": "warning",
                },
            ],
            onclick=[
                lambda: on_change_unit_price_button_clicked(buy_order_id),
                lambda: on_change_traded_amount_button_clicked(buy_order_id),
                lambda: on_order_delete_button_clicked(buy_order_id),
            ],
        )

    sell_order_data = get_my_active_order(uid, "sell")
    if not sell_order_data:
        put_markdown(
            f"""
            ## 卖单

            您目前没有卖单，{link("去发布>>>", get_url_to_module(
                "publish_order", params={"order_type": "sell"}
            ), new_window=True)}
            """,
            sanitize=False,
        )
    else:
        sell_order_id = str(sell_order_data["_id"])
        put_order_detail(
            order_id=sell_order_id,
            order_type=sell_order_data["order"]["type"],
            publish_time=sell_order_data["publish_time"],
            unit_price=sell_order_data["order"]["price"]["unit"],
            total_price=sell_order_data["order"]["price"]["total"],
            total_amount=sell_order_data["order"]["amount"]["total"],
            traded_amount=sell_order_data["order"]["amount"]["traded"],
            remaining_amount=sell_order_data["order"]["amount"]["remaining"],
        )
        put_buttons(
            buttons=[
                {
                    "label": "修改价格",
                    "value": "change_unit_price",
                    "color": "success",
                },
                {
                    "label": "修改已交易数量",
                    "value": "change_traded_amount",
                    "color": "success",
                },
                {
                    "label": "删除",
                    "value": "delete",
                    "color": "warning",
                },
            ],
            onclick=[
                lambda: on_change_unit_price_button_clicked(sell_order_id),
                lambda: on_change_traded_amount_button_clicked(sell_order_id),
                lambda: on_order_delete_button_clicked(sell_order_id),
            ],
        )
