from typing import Any, Dict, Optional

from pywebio.session import eval_js, run_js


def set_footer(html: str) -> None:
    run_js(f"$('footer').html('{html}')")


def get_current_page_url() -> str:
    return "http://" + eval_js("window.location.href").split("/")[-2]


def get_base_url() -> str:
    return eval_js("window.location.href").split("?")[0]


def get_chart_width() -> int:
    # 850 为宽度上限
    return min(eval_js('document.body.clientWidth'), 850)


def get_chart_height() -> int:
    return int(get_chart_width() / 1.5)


def get_cookie() -> Optional[str]:
    cookie_str: str = eval_js("document.cookie")
    if not cookie_str:  # Cookie 字符串为空
        return ""
    cookie_dict = dict([x.split("=") for x in cookie_str.split("; ")])
    return cookie_dict["cookie"]


def set_cookie(value: str) -> None:
    run_js(f'document.cookie = "cookie={value};"')


def jump_to(url: str) -> None:
    run_js(f"window.location.href = '{url}'")


def close_page() -> None:
    run_js("window.close()")


def get_url_params() -> Dict[str, str]:
    cookie_str = eval_js("window.location.href")
    result: Dict[str, str] = dict([
        x.split("=")
        for x in cookie_str.split("?")[1].split("&")
    ])
    if result.get("app"):  # 去除子页面参数
        del result["app"]
    return result


def set_url_params(url: str, params: Dict[str, Any]) -> str:
    params_str: str = "&".join([
        f"{key}={value}"
        for key, value in params.items()
    ])
    if "?" not in url:
        if not url.endswith("/"):
            return url + "/?" + params_str
        else:
            return url + "?" + params_str
    else:
        return url + "&" + params_str
