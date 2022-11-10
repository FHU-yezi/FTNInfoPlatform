from pywebio.output import put_markdown, put_tabs, put_warning

from data.order import get_active_orders_list
from data.token import Token
from utils.exceptions import TokenNotExistError
from utils.page import get_token
from widgets.order import put_order_item

NAME: str = "意向单列表"
DESC: str = "查看系统中已有的意向单"
VISIBILITY: bool = True


def order_list() -> None:
    try:
        user = Token.from_token_value(get_token()).user
    except TokenNotExistError:
        # 这个页面并不强制要求用户登录
        user = None

    put_markdown("# 意向单列表")
    put_warning("以下意向单均为用户自主发布，请自行核对其真实性，谨防上当受骗")

    buy_view = []
    for buy_order in get_active_orders_list("buy", 20):
        buy_view.append(put_order_item(buy_order, user))
    if not buy_view:
        buy_view.append(put_markdown("系统中暂无意向单，去发布一个？"))

    sell_view = []
    for sell_order in get_active_orders_list("sell", 20):
        sell_view.append(put_order_item(sell_order, user))
    if not sell_view:
        sell_view.append(put_markdown("系统中暂无意向单，去发布一个？"))

    put_tabs(
        [
            {"title": "买单", "content": buy_view},
            {"title": "卖单", "content": sell_view},
        ]
    )
