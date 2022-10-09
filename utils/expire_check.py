from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from data.order import get_all_trading_orders_list, set_order_expired


def expire_check_job() -> None:
    now_time = datetime.now()
    for item in get_all_trading_orders_list("all"):
        if item["expire_time"] < now_time:
            set_order_expired(str(item["_id"]))


scheduler = BackgroundScheduler()
# 每小时执行一次
scheduler.add_job(expire_check_job, "cron", hour="0-23")
