from __future__ import absolute_import, unicode_literals

import requests
import os
from celery import shared_task, group
from celery.task.schedules import crontab
from celery.decorators import periodic_task
from django.core.mail import mail_admins, EmailMessage
from django.conf import settings
from .utils import make_csv
from .models import Repository, IntervalCheckpoint, CheckpointFile
import datetime

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO





@shared_task
def send_test_email_task():
    mail_admins(
        'MailHog Test',
        'Hello from Mailhog.',
        fail_silently=False,)

r"""
Responsible: Sattar Stamkukov <devishot>


Create a task that will fetch hottest repositories from github per day, week, month (say 500), group them by language and put the result to the csv file

Implementation Details:

1. Create self containable task called `produce_hot_repo_report_task(ref_date, period='week')`

2. Investigate how and then use github api service https://developer.github.com/v3/search/#search-repositories

3. Return filepath where the result is stored /media/...

4. Define method `produce_hot_repo_report_task_for_week(period='week')`
that will call produce_hot_repo_report_task with date today()

Bonus tasks for readers:

1. Modify code so that if the result for that date is already exists, no need to send external request

2. What if we need to produce csv per language?
hint: For that you need to use celery.canvas.group and modify `produce_hot_repo_report_task(language/topic, ref_date, period='week')`

3. Probably your client wants it to be automatically callable each day at 00:00, generate report for previous date and send it to dummy email.
hint: periodic tasks

Required Libraries:
    requests
    django.core.mail
"""

@shared_task
def fetch_hot_repos(since, per_page, page):
    payload = {
        'sort': 'stars', 'order': 'desc', 'q': 'created:>={date}'.format(date=since),
        'per_page': per_page, 'page': page,
        'access_token': settings.GITHUB_OAUTH}
    headers = {'Accept': 'application/vnd.github.v3+json'}
    connect_timeout, read_timeout = 5.0, 30.0
    r = requests.get(
        'https://api.github.com/search/repositories',
        params=payload,
        headers=headers,
        timeout=(connect_timeout, read_timeout))
    items = r.json()[u'items']
    return [Repository(item) for item in items]

@shared_task
def produce_hot_repo_report_task(ref_date):
    # 1. parse date
    str_date = None
    if ref_date in ('day', 'week', 'month'):
        now = datetime.date.today()
        delta = None
        if ref_date is 'day':
            delta = datetime.timedelta(days=1)
        elif ref_date is 'week':
            delta = datetime.timedelta(weeks=1)
        else:
            delta = datetime.timedelta(days=30)
        str_date = (now - delta).isoformat()

    elif type(ref_date) is str:
        str_date = ref_date

    elif type(ref_date) is datetime.date:
        str_date = ref_date.isoformat()

    # 2. fetch and join
    job = group([
        fetch_hot_repos.s(str_date, 100, 1),
        fetch_hot_repos.s(str_date, 100, 2),
        fetch_hot_repos.s(str_date, 100, 3),
        fetch_hot_repos.s(str_date, 100, 4),
        fetch_hot_repos.s(str_date, 100, 5)
    ])
    result = job.apply_async()
    all_repos = []
    for repo in result.get():
        all_repos += repo

    # 3. group by language
    grouped_repos = {}
    for repo in all_repos:
        if repo.language in grouped_repos:
            grouped_repos[repo.language].append(repo.name)
        else:
            grouped_repos[repo.language] = [repo.name]

    # 4. create csv
    lines = []
    for lang in sorted(grouped_repos.keys()):
        lines.append([lang] + grouped_repos[lang])

    filename = '{media}/github-hot-repos-{date}.csv'.format(media=settings.MEDIA_ROOT, date=str_date)
    return make_csv(filename, lines)


"""
Responsible: Mailubayev Yernar <mailubai@gmail.com>

Create a logging handler that will be able to track Server errors (50X) and report them to admins through via celery. I advice to thoroughly understand https://docs.djangoproject.com/en/1.11/howto/error-reporting/

Seems like you need to extend default  'django.utils.log.AdminEmailHandler',


Implementation Details:

1. Create self containable task called `report_error_task/4 similar to `self.send_mail(subject, message, fail_silently=True, html_message=html_message)``

2. Extend 'django.utils.log.AdminEmailHandler' in the way it will call report_error_task.delay with the required parameters

3. Return nothing (Ensure that ignore_result flag set to True)

4. Provide http tests that ensures that it is called

Bonus tasks for readers:

1. Modify code so that task could be scheduled once per time range (1 hour, 6 hours) and all bugs will be collected and send as one email, rather than notifying often.
Hint: you also need to create models.py that will store the HttpErrorEntries


Required Libraries:
    django.core.mail
    django.util.log
    mailhog
    pytest
"""


@shared_task
def report_error_task(subject, message, *args, **kwargs):
    mail_admins(subject, message, *args, **kwargs)


@shared_task
def register_error_for_admin(subject, message, *args, **kwargs):
    """Registers error by storing result to a file"""
    chk_file = CheckpointFile.error_file(subject)
    chk_file.write(message)


@periodic_task(run_every=(crontab(hour="*", minute="*", day_of_week="*")))
def report_scheduled_error_task():
    errors_content = StringIO()
    at_least_one_flag = False
    for chk_file in CheckpointFile.read_relevant_error_files():
        header_text = "--" * 10 + " %s " % chk_file.filename + "--" * 10
        # head
        errors_content.write(header_text)
        errors_content.write(os.linesep)
        # body
        errors_content.write(chk_file.read())
        # tail
        errors_content.write(os.linesep * 5)
        at_least_one_flag = True

    if not at_least_one_flag:
        return

    email = EmailMessage(
        subject="Error report",
        body="Scheduled error report for admin",
        from_email=settings.SERVER_EMAIL,
        to=[a[1] for a in settings.ADMINS])
    email.content_subtype = "html"
    email.attach("error_dump.log", errors_content.getvalue(), 'text/plain')
    email.send()

    error_dir = '{media}/errors/'.format(media=settings.MEDIA_ROOT)
    IntervalCheckpoint.update_current(error_dir)
