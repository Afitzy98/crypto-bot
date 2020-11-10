from settings import DB_URI

from cryptobot import sched
from .strategy import hourly_task


def add_job(func, kwargs):
    name = kwargs["symbol"]
    job = sched.add_job(func, "cron", name=name, minute="0", second="15", kwargs=kwargs)
    send_message(f"✅ Started trading with {name}USDT")


def get_jobs():
    jobs = sched.get_jobs()
    if len(jobs) > 0:
        out = "💸 Currently trading with:"
        for job in jobs:
            out += f"\n\u2022 {job.name}USDT"
        send_message(out)
    else:
        send_message("0️⃣ There is currently nothing being traded.")


def remove_job(name: str):
    jobs = sched.get_jobs()
    for job in jobs:
        if job.name == name:
            scheduler.remove_job(job.id)
            send_message(f"🛑 Stopped trading with {name}USDT")