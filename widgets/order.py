from datetime import datetime
from typing import Literal

from pywebio.output import (
    put_button,
    put_collapse,
    put_markdown,
    put_processbar,
    put_row,
)


def put_order_item(
    order_id: str,
    publish_time: datetime,
    publisher_name: str,
    unit_price: float,
    total_amount: int,
    traded_amount: int,
    remaining_amount: int,
    is_mine: bool,
):
    return put_collapse(
        title=f"单价 {unit_price} / 剩余 {remaining_amount} 个",
        content=[
            put_button(
                "我的",
                color="success",
                small=True,
                onclick=lambda: None,
            )
            if is_mine
            else put_markdown(""),
            put_markdown(
                f"""
                发布时间：{publish_time}
                发布者：{publisher_name}
                已交易 / 总量：{traded_amount} / {total_amount}
                """
            ),
            put_row(
                [
                    put_markdown("交易进度："),
                    put_processbar(
                        f"trade-process-{order_id}",
                        init=round(traded_amount / total_amount, 3),
                    ),
                    None,
                ],
                size="auto 2fr 1fr",
            ),
        ],
    )


def put_order_detail(
    order_id: str,
    order_type: Literal["buy", "sell"],
    publish_time: datetime,
    unit_price: float,
    total_price: float,
    total_amount: int,
    traded_amount: int,
    remaining_amount: int,
) -> None:
    put_markdown(
        f"""
        ## {'买单'if order_type == "buy" else '卖单'}

        发布时间：{publish_time}
        单价：{unit_price}
        已交易 / 总量：{traded_amount} / {total_amount}
        剩余：{remaining_amount}
        总价：{total_price}
        """
    )
    put_row(
        [
            put_markdown("交易进度："),
            put_processbar(
                f"trade-process-{order_id}",
                init=round(traded_amount / total_amount, 3),
            ),
            None,
        ],
        size="auto 2fr 1fr",
    )
