from data.order import get_active_orders_list
from data.token import verify_token
from data.user import get_jianshu_bind_url
from pywebio.output import put_markdown, put_tabs, put_warning
from utils.exceptions import TokenNotExistError
from utils.page import get_token, is_Android
from widgets.order import put_order_item

NAME: str = "意向单列表"
DESC: str = "查看系统中已有的意向单"
VISIBILITY: bool = True


def order_list() -> None:
    try:
        uid: str = verify_token(get_token())
    except TokenNotExistError:
        # 这个页面并不强制要求用户登录
        uid: str = ""

    put_markdown("# 意向单列表")
    put_warning("以下意向单均为用户自主发布，请自行核对其真实性，谨防上当受骗")

    buy_view = []
    for buy_order_data in get_active_orders_list("buy", 20):
        buy_view.append(
            put_order_item(
                publish_time=buy_order_data["publish_time"],
                publisher_name=buy_order_data["user"]["name"],
                unit_price=buy_order_data["order"]["price"]["unit"],
                total_amount=buy_order_data["order"]["amount"]["total"],
                traded_amount=buy_order_data["order"]["amount"]["traded"],
                remaining_amount=buy_order_data["order"]["amount"]["remaining"],
                is_mine=buy_order_data["user"]["id"] == uid,
                jianshu_url=get_jianshu_bind_url(buy_order_data["user"]["id"]),
                is_Android=is_Android(),
            )
        )
    if not buy_view:
        buy_view.append(put_markdown("系统中暂无意向单，去发布一个？"))

    sell_view = []
    for sell_order_data in get_active_orders_list("sell", 20):
        sell_view.append(
            put_order_item(
                publish_time=sell_order_data["publish_time"],
                publisher_name=sell_order_data["user"]["name"],
                unit_price=sell_order_data["order"]["price"]["unit"],
                total_amount=sell_order_data["order"]["amount"]["total"],
                traded_amount=sell_order_data["order"]["amount"]["traded"],
                remaining_amount=sell_order_data["order"]["amount"]["remaining"],
                is_mine=sell_order_data["user"]["id"] == uid,
                jianshu_url=get_jianshu_bind_url(sell_order_data["user"]["id"]),
                is_Android=is_Android(),
            )
        )
    if not sell_view:
        sell_view.append(put_markdown("系统中暂无意向单，去发布一个？"))

    put_tabs(
        [
            {"title": "买单", "content": buy_view},
            {"title": "卖单", "content": sell_view},
        ]
    )
