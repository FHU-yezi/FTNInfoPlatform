from typing import Any, Dict, List

import pyecharts.options as opts
from pyecharts.charts import Line, Pie
from pyecharts.globals import CurrentConfig

from utils.config import config
from utils.page import get_chart_height, get_chart_width

# 设置 PyEcharts CDN
CurrentConfig.ONLINE_HOST = config.deploy.pyecharts_cdn


def single_line_chart(x: List, y: List, y_name: str, global_opts: List[Dict[str, Any]]):
    return (
        Line(
            init_opts=opts.InitOpts(
                width=f"{get_chart_width()}px", height=f"{get_chart_height()}px"
            )
        )
        .add_xaxis(x)
        .add_yaxis(y_name, y, is_smooth=True)
        .set_global_opts(**global_opts)
    ).render_notebook()


def double_line_chart(
    x: List,
    y1: List,
    y1_name: str,
    y2: List,
    y2_name: str,
    global_opts: List[Dict[str, Any]],
):
    return (
        Line(
            init_opts=opts.InitOpts(
                width=f"{get_chart_width()}px", height=f"{get_chart_height()}px"
            )
        )
        .add_xaxis(x)
        .add_yaxis(y1_name, y1, is_smooth=True)
        .add_yaxis(y2_name, y2, is_smooth=True)
        .set_global_opts(**global_opts)
    ).render_notebook()


def pie_chart(series_name: str, data_pair: List, global_opts: List[Dict[str, Any]]):
    return (
        Pie(
            init_opts=opts.InitOpts(
                width=f"{get_chart_width()}px", height=f"{get_chart_height()}px"
            )
        )
        .add(series_name, data_pair)
        .set_global_opts(**global_opts)
    ).render_notebook()
