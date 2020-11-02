from apscheduler.schedulers.background import BackgroundScheduler

from .strategy import hourly_task
from .telegram import send_message

sched = BackgroundScheduler()


def add_job(func, kwargs: dict):
    sched.add_job(func, "cron", minute="0", second="30", kwargs=kwargs)


def start():
    add_job(hourly_task, kwargs={"symbol": "XTZ"})
    sched.start()
    send_message("Scheduler has started")


def shutdown():
    sched.shutdown(wait=False)
    send_message("Scheduler has shutdown")
