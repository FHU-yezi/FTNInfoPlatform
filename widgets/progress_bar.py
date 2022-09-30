from pywebio.output import put_html


def put_progress_bar(current: int, max: int):
    return put_html(f'<progress value="{current}", max="{max}"></progress>').style(
        "height: 24px;"  # 默认行高
    )
