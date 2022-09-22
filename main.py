from typing import Callable, List

from pywebio import start_server
from pywebio.output import put_markdown

from utils.config import config
from utils.html import link
from utils.module_finder import Module, get_all_modules_info
from utils.page import get_base_url
from utils.patch import patch_all

modules_list = get_all_modules_info(config.base_path)


def get_jump_link(base_url: str, module_name: str) -> str:
    return link("点击跳转>>", f"{base_url}?app={module_name}", new_window=True)


def index() -> None:
    put_markdown(f"""
    # 取个名字

    版本：{config.version}
    """)

    config.refresh()  # 刷新配置文件

    content: str = ""
    for module in modules_list:
        if module.page_func_name == "index":  # 首页
            continue
        content += (f"**{module.page_name}**   "
                    f"{get_jump_link(get_base_url(), module.page_func_name)}\n\n"
                    f"{module.page_desc}\n\n")

    # 必须传入 sanitize=False 禁用 XSS 攻击防护
    # 否则 target="_blank" 属性会消失，无法实现新标签页打开
    put_markdown(content, sanitize=False)


# 将主页函数加入列表
modules_list.append(Module(
    page_func_name="index",
    page_func=index,
    page_name="取个名字",
    page_desc="我们需要一个名字"
))
patched_modules_list: List[Module] = [patch_all(module) for module in modules_list]
func_list: List[Callable[[], None]] = [x.page_func for x in patched_modules_list]

start_server(func_list, host="0.0.0.0", port=config.deploy.port, cdn=config.deploy.pywebio_cdn)
