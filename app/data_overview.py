import pyecharts.options as opts
from pywebio.output import put_html, put_markdown, put_tabs
from utils.chart import single_line_chart
from data.overview import (
    get_active_orders_count,
    get_finished_orders_count,
    get_per_hour_trade_avg_price,
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

    put_markdown("# 24 小时意向价格")
    per_hour_buy_avg_price = get_per_hour_trade_avg_price("buy", 24)
    per_hour_sell_avg_price = get_per_hour_trade_avg_price("sell", 24)
    buy_x = [str(item["_id"]) for item in per_hour_buy_avg_price]
    buy_y = [item["avg_price"] for item in per_hour_buy_avg_price]
    sell_x = [str(item["_id"]) for item in per_hour_sell_avg_price]
    sell_y = [str(item["avg_price"]) for item in per_hour_sell_avg_price]
    put_tabs(
        [
            {
                "title": "买单",
                "content": put_html(
                    single_line_chart(
                        buy_x,
                        buy_y,
                        "24 小时买单价格",
                        {"yaxis_opts": opts.AxisOpts(min_=0.08, max_=0.12)},
                        in_tab=True,
                    )
                ),
            },
            {
                "title": "卖单",
                "content": put_html(
                    single_line_chart(
                        sell_x,
                        sell_y,
                        "24 小时卖单价格",
                        {"yaxis_opts": opts.AxisOpts(min_=0.08, max_=0.12)},
                        in_tab=True,
                    )
                ),
            },
        ]
    )
