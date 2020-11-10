from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
import os

from settings import APP_SECRET_KEY, DB_URI


basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = APP_SECRET_KEY
    SCHEDULER_JOBSTORES = {
        "default": SQLAlchemyJobStore(url=DB_URI),
    }
    SCHEDULER_EXECUTORS = {
        "default": ThreadPoolExecutor(20),
        "processpool": ProcessPoolExecutor(5),
    }
    SCHEDULER_JOB_DEFAULTS = {
        "coalesce": False,
        "max_instances": 3,
        "misfire_grace_time": 3 * 60,
    }
    SCHEDULER_TIMEZONE = "UTC"

    SCHEDULER_API_ENABLED = True


class ProductionConfig(Config):
    DEBUG = False


class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class TestingConfig(Config):
    TESTING = True