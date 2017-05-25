import os
import logging
from django.conf import settings  # noqa
from celery import signals
from celery.task.control import inspect


def copy_dict(ds):
    return {k: v for k, v in ds.iteritems()}


@signals.celeryd_after_setup.connect
def configure_task_logging(instance=None, **kwargs):
    tasks = instance.app.tasks.keys()
    LOGS_DIR = settings.ROOT_DIR.path('logs')

    if not os.path.exists(str(LOGS_DIR)):
        os.makedirs(str(LOGS_DIR))
        print 'dir created'
    default_handler = {
        'level': 'DEBUG',
        'filters': None,
        'class': 'logging.handlers.WatchedFileHandler',
        'filename': ''
    }
    default_logger = {
        'handlers': [],
        'level': 'DEBUG',
        'propogate': True
    }
    LOG_CONFIG = {
        'version': 1,
        # 'incremental': True,
        'disable_existing_loggers': False,
        'handlers': {},
        'loggers': {}
    }
    for task in tasks:
        task = str(task)
        if not task.startswith('celery_uncovered.'):
            continue
        task_handler = copy_dict(default_handler)
        task_handler['filename'] = str(LOGS_DIR.path(task + ".log"))

        task_logger = copy_dict(default_logger)
        task_logger['handlers'] = [task]

        LOG_CONFIG['handlers'][task] = task_handler
        LOG_CONFIG['loggers'][task] = task_logger
    print LOG_CONFIG
    logging.config.dictConfig(LOG_CONFIG)
