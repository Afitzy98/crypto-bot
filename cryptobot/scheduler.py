import atexit

from apscheduler.executors.pool import ProcessPoolExecutor, ThreadPoolExecutor
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from pytz import utc
from settings import DB_URI

from cryptobot import app

from .constants import SYMBOLS
from .enums import JobType
from .model import get_position
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


def is_trading():
    return len([j for j in sched.get_jobs() if j.name == JobType.TRADE_MANAGER]) > 0

def add_trade_job(func, **kwargs):
    minute = "1" if app.config.get("DELAY_SCHEDULER", False) else "0" # pragma: no cover
    job = sched.add_job(
        func,
        "cron",
        hour="0",
        minute="0",
        second="15",
        name=JobType.TRADE_MANAGER,
        kwargs=kwargs,
    )


def get_jobs():
    if is_trading():
        out = "💸 Currently trading with:"
        for symbol in SYMBOLS:
            out += f"\n\u2022 {symbol}"
        send_message(out)
    else:
        send_message("0️⃣ There is currently nothing being traded.")


def is_running():
    send_message(f"Scheduler running: {sched.running}")


