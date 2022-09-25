from typing import Any, Dict, Optional

from pywebio.session import eval_js, run_js


def set_footer(html: str) -> None:
    run_js(f"$('footer').html('{html}')")


def get_base_url() -> str:
    return eval_js("window.location.href").split("?")[0]


def get_current_page_url() -> str:
    return "http://" + eval_js("window.location.href").split("/")[-2]


def get_url_to_module(module_name: str) -> str:
    return get_base_url() + f"?app={module_name}"


def get_chart_width() -> int:
    # 850 为宽度上限
    return min(eval_js("document.body.clientWidth"), 850)


def get_chart_height() -> int:
    return int(get_chart_width() / 1.5)


def get_token() -> Optional[str]:
    cookie_str: str = eval_js("document.cookie")
    if not cookie_str:  # Cookie 字符串为空
        return None
    cookie_dict = dict([x.split("=") for x in cookie_str.split("; ")])
    # Token 有可能为 None，这一边界情况在 Token 校验函数中有对应处理逻辑
    return cookie_dict.get("token")


def set_token(value: str) -> None:
    run_js(f'document.cookie = "token={value};"')


def jump_to(url: str) -> None:
    run_js(f"window.location.href = '{url}'")


def reload() -> None:
    run_js("location.reload()")


def close_page() -> None:
    run_js("window.close()")


def get_url_params() -> Dict[str, str]:
    url = eval_js("window.location.href")
    result: Dict[str, str] = dict([x.split("=") for x in url.split("?")[1].split("&")])
    if result.get("app"):  # 去除子页面参数
        del result["app"]
    return result


def set_url_params(url: str, params: Dict[str, Any]) -> str:
    params_str: str = "&".join([f"{key}={value}" for key, value in params.items()])
    if "?" not in url:
        if not url.endswith("/"):
            return url + "/?" + params_str
        else:
            return url + "?" + params_str
    else:
        return url + "&" + params_str
