from __future__ import absolute_import, unicode_literals

from django.core.mail import mail_admins
from celery import shared_task


@shared_task
def send_test_email_task():
    mail_admins(
        'MailHog Test',
        'Hello from Mailhog.',
        fail_silently=False,)
