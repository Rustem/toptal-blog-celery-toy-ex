from __future__ import absolute_import, unicode_literals

from django.core.mail import mail_admins
from celery import shared_task


@shared_task
def send_test_email_task():
    mail_admins(
        'MailHog Test',
        'Hello from Mailhog.',
        fail_silently=False,)



r"""

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

3. Probably your client wants it to be automatically callable each day at 00:00 and generate report for previous date.
hint: periodic tasks

Required Libraries:
    requests
    django.core.mail
"""

