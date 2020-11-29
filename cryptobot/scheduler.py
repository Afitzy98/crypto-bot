import atexit
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from pytz import utc
from settings import DB_URI

from cryptobot import app

from .telegram import send_message

jobstores = {
    "default": SQLAlchemyJobStore(url=DB_URI),
}
executors = {
    "default": ThreadPoolExecutor(20),
    "processpool": ProcessPoolExecutor(5),
}
job_defaults = {
    "misfire_grace_time": 3 * 60,
}

scheduler = BackgroundScheduler(
    jobstores=jobstores, executors=executors, job_defaults=job_defaults, timezone=utc
)


def shutdown():
    scheduler.shutdown()


atexit.register(shutdown)


def add_job(func, kwargs):
    name = kwargs["symbol"]
    job = scheduler.add_job(
        func,
        "cron",
        minute="0,5,10,15,20,25,30,35,40,45,50,55",
        second="10",
        name=name,
        kwargs=kwargs,
    )
    send_message(f"✅ Started trading with {name}USDT")


def get_jobs():
    jobs = scheduler.get_jobs()
    if len(jobs) > 0:
        out = "💸 Currently trading with:"
        for job in jobs:
            out += f"\n\u2022 {job.name}USDT"
        send_message(out)
    else:
        send_message("0️⃣ There is currently nothing being traded.")


def is_running():
    send_message(f"Scheduler running: {scheduler.running}")


def remove_job(name: str):
    jobs = scheduler.get_jobs()
    for job in jobs:
        if job.name == name:
            scheduler.remove_job(job.id)
            send_message(f"🛑 Stopped trading with {name}USDT")