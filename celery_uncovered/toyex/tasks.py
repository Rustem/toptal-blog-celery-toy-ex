from __future__ import absolute_import, unicode_literals

import requests
from celery import shared_task, group, chord
from django.core.mail import mail_admins
from django.conf import settings
from .utils import make_csv, strf_date
from .models import Repository
import datetime


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
    return items


def produce_hot_repo_report(period, ref_date=None):
    # 1. parse date
    ref_date_str = strf_date(period, ref_date=ref_date)

    # 2. fetch and join
    fetch_jobs = group([
        fetch_hot_repos.s(ref_date_str, 100, 1),
        fetch_hot_repos.s(ref_date_str, 100, 2),
        fetch_hot_repos.s(ref_date_str, 100, 3),
        fetch_hot_repos.s(ref_date_str, 100, 4),
        fetch_hot_repos.s(ref_date_str, 100, 5)
    ])
    return chord(fetch_jobs)(build_report_task.s(ref_date_str)).get()



@shared_task
def build_report_task(results, ref_date):
    all_repos = []
    for repos in results:
        all_repos += [Repository(repo) for repo in repos]

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

    filename = '{media}/github-hot-repos-{date}.csv'.format(media=settings.MEDIA_ROOT, date=ref_date)
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
