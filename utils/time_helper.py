from datetime import date, datetime, timedelta


def get_now_without_mileseconds() -> datetime:
    return datetime.now().replace(microsecond=0)


def get_today_in_datetime_obj() -> datetime:
    return datetime.fromisoformat(date.today().strftime(R"%Y-%m-%d"))


def get_datetime_after_hours(datetime_obj: datetime, offset: int) -> datetime:
    return datetime_obj + timedelta(hours=offset)


def get_nearest_expire_time(datetime_obj: datetime, effective_hours: int) -> datetime:
    return datetime_obj.replace(minute=0, second=0) + timedelta(hours=effective_hours)
