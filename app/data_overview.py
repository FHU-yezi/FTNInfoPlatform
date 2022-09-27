from pywebio.output import put_html, put_markdown
from utils.chart import double_line_chart, pie_chart, single_line_chart
from utils.data.overview import (
    get_active_orders_count,
    get_finished_orders_count,
    get_total_traded_amount,
    get_total_traded_price,
)

NAME: str = "数据概览"
DESC: str = "查看价格走势、成交量等信息"
VISIBILITY: bool = True


def data_overview() -> None:
    put_markdown("# 数据概览")

    put_markdown(
        f"""
        交易中意向单：{get_active_orders_count()} 条
        已完成意向单：{get_finished_orders_count()} 条
        总完成意向量：{get_total_traded_amount()} 简书贝 / {get_total_traded_price()} 元
        """
    )
