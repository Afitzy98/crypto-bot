import atexit
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from pytz import utc
from settings import DB_URI

from cryptobot import app

from .constants import PORTFOLIO_MANAGER
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

sched = BackgroundScheduler(
    jobstores=jobstores, executors=executors, job_defaults=job_defaults, timezone=utc
)


def shutdown():
    sched.shutdown()


atexit.register(shutdown)


def add_trade_job(func, kwargs):
    name = kwargs["symbol"]
    job_num = len(get_symbols())
    second = 15 + (5 * job_num)
    job = sched.add_job(
        func,
        "cron",
        minute="0",
        second=second,
        name=name,
        kwargs=kwargs,
    )
    send_message(f"✅ Started trading with {name}")

def add_portfolio_job(func):
    job = sched.add_job(
        func,
        "cron",
        day="1,3,5,7,9,11,13,15,17,19,21,23,25,27,29,31",
        hour="11",
        minute="45",
        name=PORTFOLIO_MANAGER,
    )

def get_jobs():
    symbols = get_symbols()
    if len(symbols) > 0:
        out = "💸 Currently trading with:"
        for symbol in symbols:
            out += f"\n\u2022 {symbol}"
        send_message(out)
    else:
        send_message("0️⃣ There is currently nothing being traded.")

def get_symbols():
    return [j.name for j in sched.get_jobs() if j.name != PORTFOLIO_MANAGER]

def is_running():
    send_message(f"Scheduler running: {sched.running}")

def does_portfolio_exist():
    return len([j.name for j in sched.get_jobs() if j.name == PORTFOLIO_MANAGER]) == 1

def remove_job(name: str):
    jobs = sched.get_jobs()
    for job in jobs:
        if job.name == name:
            sched.remove_job(job.id)
            if job.name != PORTFOLIO_MANAGER:
                send_message(f"🛑 Stopped trading with {name}")