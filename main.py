from signal import SIGTERM, signal
from typing import Callable, List

from pywebio import start_server
from pywebio.output import put_markdown

from data.overview import get_24h_traded_FTN_avg_price
from utils.config import config
from utils.expire_check import scheduler as expire_check_scheduler
from utils.log import access_logger, run_logger
from utils.module_finder import Module, get_all_modules_info
from utils.page import get_url_to_module
from utils.patch import patch_all
from widgets.card import put_app_card

modules_list = get_all_modules_info(config.base_path)

# 注册信号事件回调
# 在收到 SIGTERM 时执行访问日志强制刷新，之后退出
signal(SIGTERM, lambda _, __: run_logger.force_refresh())
signal(SIGTERM, lambda _, __: access_logger.force_refresh())
run_logger.debug("已注册事件回调")


def index() -> None:
    put_markdown(
        f"""
        # 简书贝信息交流中心

        版本：{config.version}

        **24 小时平均买 / 卖价：{get_24h_traded_FTN_avg_price("buy", missing="ignore")} / {get_24h_traded_FTN_avg_price("sell", missing="ignore")}**
        """
    )
    config.refresh()  # 刷新配置文件

    for module in modules_list:
        if not module.page_visibility:  # 模块被设为首页不可见
            continue

        put_app_card(
            name=module.page_name,
            url=get_url_to_module(module.page_func_name),
            desc=module.page_desc,
        )

    # 反馈表单
    put_app_card(
        name="反馈表单",
        url="https://wenjuan.feishu.cn/m?t=sRUTTLBWT9Fi-9tzm",
        desc="提出建议，反馈问题，可参与简书贝抽奖，综合中奖率 20%",
    )


# 将主页函数加入列表
modules_list.append(
    Module(
        page_func_name="index",
        page_func=index,
        page_name="简书贝信息交流中心",
        page_desc="提供简书贝相关信息交流服务",
        page_visibility=False,
    )
)
patched_modules_list: List[Module] = [patch_all(module) for module in modules_list]
func_list: List[Callable[[], None]] = [x.page_func for x in patched_modules_list]
run_logger.info(f"已加载 {len(func_list)} 个视图函数")

# 启动意向单过期检查任务
expire_check_scheduler.start()
run_logger.info("意向单过期检查任务已启动")

run_logger.info("启动网页服务......")
start_server(
    func_list, host="0.0.0.0", port=config.deploy.port, cdn=config.deploy.pywebio_cdn
)
