from data.order import (
    delete_order,
    get_my_active_order,
    get_my_finished_orders_list,
)
from data.token import create_token, verify_token
from data.user import get_jianshu_bind_url
from pywebio.output import (
    close_popup,
    popup,
    put_buttons,
    put_markdown,
    put_tabs,
    toast,
)
from utils.exceptions import TokenNotExistError
from utils.html import link
from utils.login import require_login
from utils.page import get_token, get_url_to_module, jump_to, reload, set_token
from widgets.order import put_finished_order_item, put_order_detail

NAME: str = "我的意向单"
DESC: str = "查看并修改自己的意向单"
VISIBILITY: bool = True


def on_delete_confirmed(order_id: str) -> None:
    delete_order(order_id)
    toast("删除成功", color="success")
    reload(delay=1)


def on_change_unit_price_button_clicked(order_id: str) -> None:
    jump_to(
        get_url_to_module(
            "change_unit_price",
            {"order_id": order_id},
        ),
    )


def on_change_traded_amount_button_clicked(order_id: str) -> None:
    jump_to(
        get_url_to_module(
            "change_traded_amount",
            {"order_id": order_id},
        ),
    )


def on_order_delete_button_clicked(order_id: str) -> None:
    with popup("确认删除", size="large"):
        put_markdown(
            """
            确认要删除这条意向单吗？

            删除后，该意向单将从列表中消失，并且**不会**显示在下方的“已完成”列表中。

            如果您已经完成了该意向单的交易，请点击“修改已交易数量”按钮，并将“已交易”输入框的数值改为与总量相同的值。
            """
        )
        put_buttons(
            buttons=[
                {
                    "label": "确认",
                    "value": "confirm",
                    "color": "warning",
                },
                {
                    "label": "取消",
                    "value": "cancel",
                },
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

    if not get_jianshu_bind_url(uid):
        put_markdown(
            "绑定简书账号，成交更快，"
            + link("去绑定>>>", get_url_to_module("personal_center"), new_window=True),
            sanitize=False,
        )

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

    put_markdown(
        """
        ## 已完成

        仅展示最近 20 条
        """
    )

    finished_buy_view = []
    for finished_buy_order_data in get_my_finished_orders_list(uid, "buy", 20):
        finished_buy_view.append(
            put_finished_order_item(
                publish_time=finished_buy_order_data["publish_time"],
                finish_time=finished_buy_order_data.get("finish_time", "不可用"),
                unit_price=finished_buy_order_data["order"]["price"]["unit"],
                total_price=finished_buy_order_data["order"]["price"]["total"],
                total_amount=finished_buy_order_data["order"]["amount"]["total"],
            )
        )
    if not finished_buy_view:
        finished_buy_view.append(put_markdown("您没有已完成的买单"))

    finished_sell_view = []
    for finished_sell_order_data in get_my_finished_orders_list(uid, "sell", 20):
        finished_sell_view.append(
            put_finished_order_item(
                publish_time=finished_sell_order_data["publish_time"],
                finish_time=finished_sell_order_data.get("finish_time", "不可用"),
                unit_price=finished_sell_order_data["order"]["price"]["unit"],
                total_price=finished_sell_order_data["order"]["price"]["total"],
                total_amount=finished_sell_order_data["order"]["amount"]["total"],
            )
        )
    if not finished_sell_view:
        finished_sell_view.append(put_markdown("您没有已完成的卖单"))

    put_tabs(
        [
            {"title": "买单", "content": finished_buy_view},
            {"title": "卖单", "content": finished_sell_view},
        ]
    )
