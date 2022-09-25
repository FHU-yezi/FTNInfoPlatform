from typing import Callable, List

from pywebio import start_server
from pywebio.output import put_markdown

from utils.config import config
from utils.html import link
from utils.module_finder import Module, get_all_modules_info
from utils.page import get_url_to_module
from utils.patch import patch_all

modules_list = get_all_modules_info(config.base_path)


def get_jump_link(module_name: str) -> str:
    return link("点击跳转>>", get_url_to_module(module_name), new_window=True)


def index() -> None:
    put_markdown(
        f"""
        # 简书贝信息交流中心

        版本：{config.version}
        """
    )

    config.refresh()  # 刷新配置文件

    content: str = ""
    for module in modules_list:
        if not module.page_visibility:  # 模块被设为首页不可见
            continue
        content += (
            f"**{module.page_name}**   "
            f"{get_jump_link(module.page_func_name)}\n\n"
            f"{module.page_desc}\n\n"
        )

    # 必须传入 sanitize=False 禁用 XSS 攻击防护
    # 否则 target="_blank" 属性会消失，无法实现新标签页打开
    put_markdown(content, sanitize=False)


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

start_server(
    func_list, host="0.0.0.0", port=config.deploy.port, cdn=config.deploy.pywebio_cdn
)
