from pywebio.output import put_button


def put_badge(label: str, color: str):
    return put_button(
        label,
        color=color,
        small=True,
        onclick=lambda: None,
    )
