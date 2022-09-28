from pywebio.output import (
    put_button,
    put_collapse,
    put_markdown,
    put_tabs,
    put_row,
    put_processbar,
)
from data.order import get_active_orders_list
from data.token import verify_token
from utils.exceptions import TokenNotExistError
from utils.page import get_token

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

    buy_view = []
    for item in get_active_orders_list("buy", 20):
        buy_view.append(
            put_collapse(
                title=f"单价 {item['order']['price']['unit']} / 剩余 {item['order']['amount']['remaining']} 个",
                content=[
                    put_button("我的", color="success", small=True, onclick=lambda: None)
                    if item["user"]["id"] == uid
                    else put_markdown(""),
                    put_markdown(
                        f"""
                        发布时间：{item['publish_time']}
                        发布者：{item['user']['name']}
                        已交易 / 总数：{item['order']['amount']['traded']} / {item['order']['amount']['total']}
                        """
                    ),
                    put_row(
                        [
                            put_markdown("交易进度："),
                            put_processbar(
                                f"trade-process-bar-{item['_id']}",
                                init=round(
                                    item["order"]["amount"]["traded"]
                                    / item["order"]["amount"]["total"],
                                    3,
                                ),
                            ),
                        ],
                        size="auto 3fr",
                    ),
                ],
            )
        )
    if not buy_view:
        buy_view.append(put_markdown("系统中暂无意向单，去发布一个？"))

    sell_view = []
    for item in get_active_orders_list("sell", 20):
        sell_view.append(
            put_collapse(
                title=f"单价 {item['order']['price']['unit']} / 剩余 {item['order']['amount']['remaining']} 个",
                content=[
                    put_button("我的", color="success", small=True, onclick=lambda: None)
                    if item["user"]["id"] == uid
                    else put_markdown(""),
                    put_markdown(
                        f"""
                        发布时间：{item['publish_time']}
                        发布者：{item['user']['name']}
                        已交易 / 总数：{item['order']['amount']['traded']} / {item['order']['amount']['total']}
                        """
                    ),
                    put_row(
                        [
                            put_markdown("交易进度："),
                            put_processbar(
                                f"trade-process-bar-{item['_id']}",
                                init=round(
                                    item["order"]["amount"]["traded"]
                                    / item["order"]["amount"]["total"],
                                    3,
                                ),
                            ),
                        ],
                        size="auto 3fr",
                    ),
                ],
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
