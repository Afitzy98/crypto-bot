from apscheduler.schedulers.background import BackgroundScheduler

from .telegram import send_message

sched = BackgroundScheduler()


def start():
    sched.add_job(send_message, "cron", minute="1-59", kwargs={"message": "Running..."})
    sched.start()
    send_message("Scheduler has started")


def shutdown():
    sched.shutdown(wait=False)
    send_message("Scheduler has shutdown")
