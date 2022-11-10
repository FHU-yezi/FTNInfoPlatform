from apscheduler.schedulers.background import BackgroundScheduler

from data.order_new import get_active_orders_list


def expire_check_job() -> None:
    for order in get_active_orders_list("all", 10 ** 4):
        if order.is_expired:
            order.expire()


scheduler = BackgroundScheduler()
# 每小时执行一次
scheduler.add_job(expire_check_job, "cron", hour="0-23")
