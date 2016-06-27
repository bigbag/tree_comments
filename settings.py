import os

from helpers.logging import setup_loggers


class Config(object):
    PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

    APP_HOST = '0.0.0.0'
    APP_PORT = 7777

    # DATABASES
    SQLALCHEMY_USER = 'user'
    SQLALCHEMY_PASSWORD = 'password'
    SQLALCHEMY_DB = 'comment'
    SQLALCHEMY_HOST = '127.0.0.1'
    SQLALCHEMY_PORT = 3306
    SQLALCHEMY_ECHO = False

    DB_CONFIG = {
        'user': SQLALCHEMY_USER,
        'password': SQLALCHEMY_PASSWORD,
        'db': SQLALCHEMY_DB,
        'host': SQLALCHEMY_HOST,
        'port': SQLALCHEMY_PORT,
        'echo': SQLALCHEMY_ECHO,
    }

    # TEMP
    TEMP_DIR = os.path.join(PROJECT_ROOT, 'tmp')

    # LOGGING
    LOG_ENABLE = True
    LOG_LEVEL = 'ERROR'
    LOG_MAX_SIZE = 1024 * 1024
    LOG_DIR = os.path.join(PROJECT_ROOT, 'logs')
    LOG_SETTINGS = {
        'version': 1,
        'formatters': {
            'default': {
                'format': '[%(levelname)s] [P:%(process)d] [%(asctime)s] %(pathname)s:%(lineno)d: %(message)s',
                'datefmt': '%d/%b/%Y %H:%M:%S',
            },
            'simple': {
                'format': '[%(levelname)s] [%(asctime)s] %(message)s',
                'datefmt': '%d/%b/%Y %H:%M:%S',
            },
        }
    }

    setup_loggers(LOG_SETTINGS, LOG_ENABLE, LOG_LEVEL, LOG_DIR, LOG_MAX_SIZE)
