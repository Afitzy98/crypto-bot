from apscheduler.schedulers.blocking import BlockingScheduler
from threading import Thread
from typing import Callable
from .telegram import sendMessage

class Scheduler(Thread):
    def __init__(self):
        super(Scheduler, self).__init__()
        self.sched = BlockingScheduler()

    def add_hourly_job():
        self.sched.add_job(lambda: sendMessage("Running"), "cron", minutes="1-59")

    def add_job_on_hours(task: Callable, hours: str):
        self.sched.add_job(task, "cron", hour=hours)

    def run(self):
        # if(len(self.sched.get_jobs())):
        self.add_hourly_job()
        self.sched.start()
        sendMessage("Scheduler has started")
        # else:
        #     sendMessage("There are no jobs for the scheduler to start")

    
    def pause(self):
        self.sched.pause()

    def resume(self):
        self.sched.resume()

    def shutdown(self):
        self.sched.shutdown(wait=False)
        sendMessage("Scheduler has shutdown")
