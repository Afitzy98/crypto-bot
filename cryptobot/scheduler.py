from apscheduler.schedulers.background import BackgroundScheduler

from .strategy import apply_strategy
from .telegram import send_message

sched = BackgroundScheduler()

def start():
    sched.add_job(apply_strategy, "cron", minute="0", second="30" kwargs={"symbol": "LINKUSDT"})
    sched.start()
    send_message("Scheduler has started")


def shutdown():
    sched.shutdown(wait=False)
    send_message("Scheduler has shutdown")
