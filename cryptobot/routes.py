from flask import request
import atexit

from settings import TG_BOT_TOKEN, TG_USER_ID

from cryptobot import app
from .scheduler import BackgroundScheduler, executors, job_defaults, jobstores, utc
from .strategy import hourly_task
from .telegram import send_message

scheduler = None


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


switcher = {"start": add_job, "stop": remove_job, "list": get_jobs}


def handle_message(message: str):

    parts = message.split()

    func = switcher.get(
        parts[0].lower(),
        lambda: send_message(f"Sorry I didn't understand that, you said: {message}"),
    )

    if func.__code__.co_argcount == 0:
        func()
    elif func.__code__.co_argcount == 1:
        func(parts[1])
    else:
        func(hourly_task, kwargs={"symbol": parts[1]})


def handle_request(req: dict):
    message = req["message"]
    # if the update is a message and the message was from my telegram account proceed
    if message and message["from"]["id"] == TG_USER_ID:
        return handle_message(message["text"])


@app.route("/", methods=["GET"])
def keep_alive():
    return "ok"


@app.route("/{}".format(TG_BOT_TOKEN), methods=["POST"])
def webhook_endpoint():
    try:
        req = request.get_json()
        handle_request(req)
        return "ok"
    except Exception as e:
        return str(e)


@app.before_first_request
def init_scheduler():
    global scheduler
    scheduler = BackgroundScheduler(
        jobstores=jobstores,
        executors=executors,
        job_defaults=job_defaults,
        timezone=utc,
    )
    if scheduler is not None and not scheduler.running:
        scheduler.start()
        send_message("🔄 Scheduler has restarted")
    # Shut down the scheduler when exiting the app
    atexit.register(lambda: scheduler.shutdown())
