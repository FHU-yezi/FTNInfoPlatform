from typing import Dict, List, Literal

from pywebio.output import put_button, put_collapse, put_markdown, put_tabs
from utils.auth import get_uid_from_cookie
from utils.db import trade_data_db
from utils.page import get_cookie

NAME: str = "意向单列表"
DESC: str = "查看系统中已有的意向单"
VISIBILITY: bool = True
uid: str = ""  # TODO


def get_order_list(order_type: Literal["buy", "sell"]) -> List[Dict]:
    return (
        # TODO
        trade_data_db
        .find({"order.type": order_type})
        .sort([("price.single", -1 if order_type == "buy" else 1)])
        .limit(20)
    )


def order_list() -> None:
    global uid
    uid = get_uid_from_cookie(get_cookie())

    put_markdown("# 意向单列表")

    buy_view = []
    for item in get_order_list("buy"):
        buy_view.append(put_collapse(
            title=f"单价 {item['order']['price']['single']} / 剩余 {item['order']['amount']['remaining']} 个",
            content=[
                put_button("我的", color="success", small=True, onclick=lambda: None) if item['user']['id'] == uid else put_markdown(""),
                put_markdown(f"""
                发布时间：{item['publish_time']}
                发布者：{item['user']['name']}
                已交易 / 总数：{item['order']['amount']['traded']} / {item['order']['amount']['total']}
                """)
            ]
        ))

    sell_view = []
    for item in get_order_list("sell"):
        sell_view.append(put_collapse(
            title=f"单价 {item['order']['price']['single']} / 剩余 {item['order']['amount']['remaining']} 个",
            content=[
                put_button("我的", color="success", small=True, onclick=lambda: None) if item['user']['id'] == uid else put_markdown(""),
                put_markdown(f"""
                发布时间：{item['publish_time']}
                发布者：{item['user']['name']}
                已交易 / 总数：{item['order']['amount']['traded']} / {item['order']['amount']['total']}
                """)
            ]
        ))

    put_tabs([
        {"title": "我要卖贝", "content": buy_view},
        {"title": "我要买贝", "content": sell_view}
    ])
