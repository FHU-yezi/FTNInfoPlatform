from typing import Optional

from pywebio.session import eval_js, run_js


def set_footer(html: str) -> None:
    run_js(f"$('footer').html('{html}')")


def get_current_page_url() -> str:
    return "http://" + eval_js("window.location.href").split("/")[-2]


def get_chart_width() -> int:
    # 850 为宽度上限
    return min(eval_js('document.body.clientWidth'), 850)


def get_chart_height() -> int:
    return int(get_chart_width() / 1.5)


def get_cookie() -> Optional[str]:
    return eval_js("document.cookie").split(";")[0].split("=")[1]


def set_cookie(value: str) -> None:
    run_js(f'document.cookie = "cookie={value};"')
