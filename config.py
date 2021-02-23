import os

from settings import APP_SECRET_KEY

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = APP_SECRET_KEY
    DELAY_SCHEDULER = False


class ProductionConfig(Config):
    DEBUG = True # ** TURNING ON DEBUG MODE FOR PRODUCTION WHILE WORKING OUT KINKS, REMOVE THIS EVENTUALLY


class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    DELAY_SCHEDULER = True


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    DELAY_SCHEDULER = True


class TestingConfig(Config):
    DEVELOPMENT = True
    TESTING = True
    DELAY_SCHEDULER = True
