from datetime import datetime
from typing import Literal

from pywebio.output import (
    put_collapse,
    put_markdown,
    put_processbar,
    put_row,
)

from widgets.badge import put_badge


def put_order_item(
    order_id: str,
    publish_time: datetime,
    publisher_name: str,
    unit_price: float,
    total_amount: int,
    traded_amount: int,
    remaining_amount: int,
    is_mine: bool,
    jianshu_url: str,
):
    jianshu_binded: bool = bool(jianshu_url)  # 判断简书 URL 字段是否为空

    return put_collapse(
        title=f"单价 {unit_price} / 剩余 {remaining_amount} 个",
        content=[
            put_row(
                [
                    put_badge("我的", color="success") if is_mine else put_markdown(""),
                    None,
                    put_badge("未绑定简书", color="warning")
                    if not jianshu_binded
                    else put_markdown(""),
                ],
                size="50px 10px 120px",
            ),
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


def put_finished_order_item(
    publish_time: datetime,
    finish_time: datetime,
    unit_price: float,
    total_price: float,
    total_amount: int,
) -> None:
    return put_collapse(
        title=f"成交于 {str(finish_time).split(' ')[0]} / 共 {total_price} 元",
        content=[
            put_markdown(
                f"""
                发布时间：{publish_time}
                单价：{unit_price}
                总量：{total_amount}
                """
            )
        ],
    )
