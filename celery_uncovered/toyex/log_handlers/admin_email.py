from django.utils.log import AdminEmailHandler as BaseAdminEmailHandler
from celery_uncovered.toyex.tasks import report_error_task


class AdminEmailHandler(BaseAdminEmailHandler):

    def send_mail(self, subject, message, *args, **kwargs):
        report_error_task.delay(subject, message, *args, **kwargs)
