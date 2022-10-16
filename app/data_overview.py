import pyecharts.options as opts
from widgets.trade import put_trade_item
from data.overview import (
    get_24h_traded_FTN_avg_price,
    get_finished_orders_count,
    get_in_trading_orders_count,
    get_recent_trade_list,
    get_per_hour_trade_avg_price,
    get_total_traded_amount,
    get_total_traded_price,
)
from pywebio.output import put_html, put_markdown, put_tabs
from utils.chart import single_line_chart

NAME: str = "数据概览"
DESC: str = "查看价格走势、成交量等信息"
VISIBILITY: bool = True


def data_overview() -> None:
    put_markdown("# 数据概览")

    put_markdown(
        f"""
        24 小时平均买 / 卖价：{get_24h_traded_FTN_avg_price("buy", missing="ignore")} / {get_24h_traded_FTN_avg_price("sell", missing="ignore")}
        交易中意向单：{get_in_trading_orders_count("all")} 条
        已完成意向单：{get_finished_orders_count("all")} 条
        总交易量：{get_total_traded_amount()} 简书贝 / {get_total_traded_price()} 元
        """
    )

    put_markdown("## 24 小时交易价格")
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
                        {
                            "yaxis_opts": opts.AxisOpts(min_=0.08, max_=0.12),
                            "legend_opts": opts.LegendOpts(is_show=False),
                        },
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
                        {
                            "yaxis_opts": opts.AxisOpts(min_=0.08, max_=0.12),
                            "legend_opts": opts.LegendOpts(is_show=False),
                        },
                        in_tab=True,
                    )
                ),
            },
        ]
    )

    put_markdown("# 近期成交")

    buy_view = []
    for buy_trade_data in get_recent_trade_list("buy"):
        buy_view.append(
            put_trade_item(
                trade_time=buy_trade_data["trade_time"],
                unit_price=buy_trade_data["unit_price"],
                trade_amount=buy_trade_data["trade_amount"],
                total_price=buy_trade_data["total_price"]
            )
        )
    if not buy_view:
        buy_view.append(put_markdown("没有近期成交的买单"))

    sell_view = []
    for sell_trade_data in get_recent_trade_list("sell"):
        sell_view.append(
            put_trade_item(
                trade_time=sell_trade_data["trade_time"],
                unit_price=sell_trade_data["unit_price"],
                trade_amount=sell_trade_data["trade_amount"],
                total_price=sell_trade_data["total_price"]
            )
        )
    if not sell_view:
        sell_view.append(put_markdown("没有近期成交的卖单"))

    put_tabs(
        [
            {"title": "买单", "content": buy_view},
            {"title": "卖单", "content": sell_view},
        ]
    )
