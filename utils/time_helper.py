from datetime import date, datetime
from typing import Dict


def get_now_without_mileseconds() -> datetime:
    return datetime.now().replace(microsecond=0)


def get_today_in_datetime_obj() -> datetime:
    return datetime.fromisoformat(date.today().strftime(r"%Y-%m-%d"))
