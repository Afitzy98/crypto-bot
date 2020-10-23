from apscheduler.schedulers.background import BackgroundScheduler
from .telegram import sendMessage

sched = BackgroundScheduler()

def start():
    sched.add_job(sendMessage, "cron", minute="1-59", kwargs={"message":"Running..."})
    sched.start()
    sendMessage("Scheduler has started")

def shutdown():
    sched.shutdown(wait=False)
    sendMessage("Scheduler has shutdown")
