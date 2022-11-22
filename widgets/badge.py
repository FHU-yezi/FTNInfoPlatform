from pywebio.output import put_widget


def put_badge(label: str, color: str):
    tpl = """
    <span class="badge badge-{{color}}" style="margin-bottom: 10px; font-size: 90%; padding: 7px 10px 7px 10px">{{label}}</span>
    """
    return put_widget(
        tpl,
        {
            "label": label,
            "color": color,
        },
    )
