from __future__ import absolute_import, unicode_literals

import requests
import os
import csv
from celery import shared_task, group
from django.core.mail import mail_admins, EmailMessage
from django.conf import settings
from .utils import is_exists, strf_date
from .models import Repository


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
def make_csv(filename, lines):
    dirname = os.path.dirname(filename)
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    with open(filename, 'wb') as csvfile:
        trending_csv = csv.writer(csvfile)
        for line in lines:
            trending_csv.writerow(line)
    return filename

@shared_task
def fetch_hot_repos(language, since, per_page, page):
    query = 'created:>={date}'.format(date=since)
    if language:
        query += ' language:{lang}'.format(lang=language)
    payload = {
        'sort': 'stars', 'order': 'desc', 'q': query,
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
def fetch_hot_repos_group(group_params):
    job = group( [fetch_hot_repos.s(*params) for params in group_params] )
    result = job.apply_async()
    return result.get()

@shared_task
def store_hot_repos_group(repos_group, filename):
    repos_flattened = []
    for repo in repos_group:
        repos_flattened += repo

    reponames_by_lang = {}
    for repo in repos_flattened:
        if repo.language in reponames_by_lang:
            reponames_by_lang[repo.language].append(repo.name)
        else:
            reponames_by_lang[repo.language] = [repo.name]

    lines = []
    for lang in sorted(reponames_by_lang.keys()):
        lines.append([lang] + reponames_by_lang[lang])
    result = make_csv.delay(filename, lines)
    return result.get()

@shared_task
def produce_hot_repo_report_task(ref_date, period=None):
    # parse date
    ref_date_str = strf_date(period, ref_date)

    # check if results exist
    filename = '{media}/github-hot-repos-{date}.csv'.format(media=settings.MEDIA_ROOT, date=ref_date_str)
    if is_exists(filename):
        return filename

    group_params = map(lambda i: (None, ref_date_str, 100, i), range(1, 5))

    chain = fetch_hot_repos_group.s(group_params) | store_hot_repos_group.s(filename)
    result = chain()
    return result.get()


@shared_task
def produce_hot_repo_report_task_for_languages(languages, ref_date, period=None):
    # 1. parse date
    ref_date_str = strf_date(period, ref_date)

    # 1b. generate filenames, skip if exists
    filenames_by_lang = {}
    for language in languages:
        filename = '{media}/github-hot-repos-{date}-{lang}.csv'.format(
            media=settings.MEDIA_ROOT,
            date=ref_date_str,
            lang=language)
        if not is_exists(filename):
            filenames_by_lang[language] = filename

    # 2. fetch and join
    languages = filenames_by_lang.keys()
    job_fetch = group( [fetch_hot_repos.s(lang, ref_date_str, 100, 1) for lang in languages] )
    result = job_fetch.apply_async()
    repo_names_by_lang = {}
    for index, repos in enumerate(result.get()):
        language = languages[index]
        repo_names_by_lang[language] = [repo.name for repo in repos]

    # 3. create csv per language
    filename_repos = [(filenames_by_lang[lang], repo_names_by_lang[lang]) for lang in languages]
    job_store = group( [make_csv.s(filename, [repo_names]) for filename, repo_names in filename_repos] )
    result = job_store.apply_async()
    return result.get()

@shared_task
def email_attachment_task(filename, title, emails=None):
    if not emails:
        emails = map(lambda x: x[1], settings.ADMINS)
    message = EmailMessage(
        title,
        'With attachment',
        'root@localhost',
        emails
    )
    message.attach_file(filename)
    message.send()

@shared_task
def send_hot_repo_daily_report_task(emails=None):
    title = 'Daily hotrepos'
    chain = produce_hot_repo_report_task.s(None, 'day') | email_attachment_task.s(title, emails)
    result = chain()
    return result.get()


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
