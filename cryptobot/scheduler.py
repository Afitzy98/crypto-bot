import atexit

from apscheduler.executors.pool import ProcessPoolExecutor, ThreadPoolExecutor
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from pytz import utc
from settings import DB_URI

from cryptobot import app

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


def add_trade_job(func, kwargs):
    name = ",".join(kwargs["symbols"])
    job = sched.add_job(
        func,
        "cron",
        hour="0",
        second="15",
        name=name,
        kwargs=kwargs,
    )

def add_portfolio_job(func):
    job = sched.add_job(
        func,
        "cron",
        day="6",
        hour="23",
        minute="45",
        name=JobType.PORTFOLIO_MANAGER,
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
    current_jobs = [j.name for j in sched.get_jobs() if j.name != JobType.PORTFOLIO_MANAGER]
    if len(current_jobs) > 0:
        name = current_jobs[0]
        return name.split(",")
    else: 
        return []

def is_running():
    send_message(f"Scheduler running: {sched.running}")


def does_portfolio_exist():
    return len([j.name for j in sched.get_jobs() if j.name == JobType.PORTFOLIO_MANAGER]) == 1


def update_symbols(next_symbols: list, task, handle_exit, timestamp):
    # get current job
    current_jobs = [j for j in sched.get_jobs() if j.name != JobType.PORTFOLIO_MANAGER]
    current_symbols = []
    if len(current_jobs) > 0:
        current_job = current_jobs[0]
        # remove the old job
        sched.remove_job(current_job.id)
        # get current symbols from job name
        current_symbols = current_job.name.split(",")
        # find the new and old symbols 


    new_symbols = [s for s in next_symbols if s not in current_symbols]
    old_symbols = [s for s in current_symbols if s not in next_symbols]

    # add new trade job
    add_trade_job(task, {"symbols":next_symbols})
    out = ""
    if len(old_symbols) > 0:
        out +="🛑 Stopped trading with: \n"
        for s in old_symbols:
            handle_exit(s, get_position(timestamp, s).position)
            out+= f"\u2022 {s}\n"
        out += "\n"

    out += "✅ Started trading with: \n"
    for s in new_symbols:
        out += f"\u2022 {s} \n"

    send_message(out)

def stop_trading(handle_exit, timestamp):
    current_jobs = [j.name for j in sched.get_jobs() if j.name != JobType.PORTFOLIO_MANAGER]
    
    if len(current_jobs) > 0:
        name = current_jobs[0]
        out = "🛑 Stopped trading with: \n"
        for s in name.split(","):
            handle_exit(s, get_position(timestamp, s).position)
            out+= f"\u2022 {s}\n"
            
        send_message(out)
    
    sched.remove_all_jobs()
    