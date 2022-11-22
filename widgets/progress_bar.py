from pywebio.output import put_widget


def put_progress_bar(current: int, max: int):
    tpl = """
    <div class="progress">
        <div class="progress-bar w-{{percent}}" role="progressbar" aria-valuenow="{{percent}}" aria-valuemin="0" aria-valuemax="100"></div>
    </div>
    """
    current_percent: int = round(current / max)
    return put_widget(
        tpl,
        {
            "percent": current_percent,
        },
    )
