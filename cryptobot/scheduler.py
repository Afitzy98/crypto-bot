from apscheduler.schedulers.background import BackgroundScheduler

from .strategy import hourly_task
from .telegram import send_message

sched = BackgroundScheduler()

def start():
    sched.add_job(hourly_task, "cron", minute="0", second="30", kwargs={"symbol": "XTZ"})
    sched.start()
    send_message("Scheduler has started")


def shutdown():
    sched.shutdown(wait=False)
    send_message("Scheduler has shutdown")
