from datetime import datetime

from pywebio.output import put_collapse, put_markdown


def put_trade_item(
    trade_time: datetime, unit_price: float, trade_amount: int, total_price: float
):
    return put_collapse(
        title=f"单价 {unit_price} / {trade_amount} 个",
        content=[
            put_markdown(
                f"""
                交易时间：{trade_time}
                总价：{total_price}
                """
            )
        ],
    )
