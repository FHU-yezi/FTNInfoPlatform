from data.order_new import Order
from data.token_new import Token
from pywebio.output import (
    close_popup,
    popup,
    put_buttons,
    put_markdown,
    put_tabs,
    put_warning,
)
from utils.exceptions import TokenNotExistError
from utils.html import link
from utils.login import require_login
from utils.page import get_token, get_url_to_module, jump_to, reload, set_token
from widgets.order import put_finished_order_item, put_order_detail
from widgets.toast import toast_success

NAME: str = "我的意向单"
DESC: str = "查看并修改自己的意向单"
VISIBILITY: bool = True


def on_delete_confirmed(order: Order) -> None:
    order.delete()
    toast_success("删除成功")
    reload(delay=1)


def on_set_all_traded_confirmed(order: Order) -> None:
    order.set_all_traded()
    toast_success("已设为全部完成")
    reload(delay=1)


def on_change_unit_price_button_clicked(order: Order) -> None:
    jump_to(
        get_url_to_module(
            "change_unit_price",
            {"order_id": order.id},
        ),
    )


def on_change_traded_amount_button_clicked(order: Order) -> None:
    jump_to(
        get_url_to_module(
            "change_traded_amount",
            {"order_id": order.id},
        ),
    )


def on_set_all_traded_button_clicked(order: Order) -> None:
    with popup("全部完成", size="large"):
        put_markdown(
            """
            确认要将这条意向单设为全部完成吗？

            操作后，该意向单将显示在下方的“已完成”列表中。

            如果您想要删除意向单，请点击“删除”按钮。
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
                lambda: on_set_all_traded_confirmed(order),
                close_popup,
            ],
        )


def on_order_delete_button_clicked(order: Order) -> None:
    with popup("确认删除", size="large"):
        put_markdown(
            """
            确认要删除这条意向单吗？

            删除后，该意向单将从列表中消失，并且**不会**显示在下方的“已完成”列表中。

            如果您已经完成了该意向单的交易，请点击“全部完成”按钮。
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
                lambda: on_delete_confirmed(order),
                close_popup,
            ],
        )


def my_orders() -> None:
    try:
        user = Token.from_token_value(get_token()).user
    except TokenNotExistError:
        user = require_login()
        token = user.generate_token()
        set_token(token.value)

    put_markdown("# 我的意向单")

    if not user.is_jianshu_binded:
        put_warning(
            put_markdown(
                "绑定简书账号后才可发布意向单，"
                + link("去绑定>>>", get_url_to_module("personal_center"), new_window=True),
                sanitize=False,
            ),
        )

    buy_order = user.buy_order
    if not buy_order:
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
        put_order_detail(buy_order)
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
                    "label": "全部完成",
                    "value": "set_all_traded",
                    "color": "success",
                },
                {
                    "label": "删除",
                    "value": "delete",
                    "color": "warning",
                },
            ],
            onclick=[
                lambda: on_change_unit_price_button_clicked(buy_order),
                lambda: on_change_traded_amount_button_clicked(buy_order),
                lambda: on_set_all_traded_button_clicked(buy_order),
                lambda: on_order_delete_button_clicked(buy_order),
            ],
        )

    sell_order = user.sell_order
    if not sell_order:
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
        put_order_detail(sell_order)
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
                    "label": "全部完成",
                    "value": "set_all_traded",
                    "color": "success",
                },
                {
                    "label": "删除",
                    "value": "delete",
                    "color": "warning",
                },
            ],
            onclick=[
                lambda: on_change_unit_price_button_clicked(sell_order),
                lambda: on_change_traded_amount_button_clicked(sell_order),
                lambda: on_set_all_traded_button_clicked(sell_order),
                lambda: on_order_delete_button_clicked(sell_order),
            ],
        )

    put_markdown(
        """
        ## 已完成

        仅展示最近 20 条
        """
    )

    finished_buy_view = []
    for finished_buy_order in user.finished_orders("buy", 20):
        finished_buy_view.append(put_finished_order_item(finished_buy_order))
    if not finished_buy_view:
        finished_buy_view.append(put_markdown("您没有已完成的买单"))

    finished_sell_view = []
    for finished_sell_order in user.finished_orders("sell", 20):
        finished_sell_view.append(put_finished_order_item(finished_sell_order))
    if not finished_sell_view:
        finished_sell_view.append(put_markdown("您没有已完成的卖单"))

    put_tabs(
        [
            {"title": "买单", "content": finished_buy_view},
            {"title": "卖单", "content": finished_sell_view},
        ]
    )
