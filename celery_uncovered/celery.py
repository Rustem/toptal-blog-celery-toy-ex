from __future__ import absolute_import

import os
from celery import Celery, signals


# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')

# django.setup()

app = Celery('celery_uncovered')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
app.conf.beat_schedule = {
    'schedule-midnight-hotrepo-report': {
        'task': 'celery_uncovered.toyex.tasks.send_hot_repo_daily_report_task',
        'schedule': 30.0
    },
}

import celery_uncovered.tricks.celery_conf
