from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from pytz import utc

from settings import DB_URI

from .telegram import send_message

jobstores = {
    "default": SQLAlchemyJobStore(url=DB_URI),
}
executors = {"default": ThreadPoolExecutor(20), "processpool": ProcessPoolExecutor(5)}
job_defaults = {"coalesce": False, "max_instances": 3, "misfire_grace_time": 3 * 60}

scheduler = BackgroundScheduler(
    jobstores=jobstores, executors=executors, job_defaults=job_defaults, timezone=utc
)


def add_job(func, kwargs):
    if not scheduler.running:
        start_scheduler()
    name = kwargs["symbol"]
    job = scheduler.add_job(
        func, "cron", name=name, minute="0", second="15", kwargs=kwargs
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


def remove_job(name: str):
    jobs = scheduler.get_jobs()
    for job in jobs:
        if job.name == name:
            scheduler.remove_job(job.id)
            send_message(f"🛑 Stopped trading with {name}USDT")


def start_scheduler():
    if not scheduler.running:
        scheduler.start()
        send_message("🔄 Restarted Scheduler")
