from django.utils.log import AdminEmailHandler as BaseAdminEmailHandler
from celery_uncovered.toyex.tasks import report_error_task, register_error_for_admin


class AdminEmailHandler(BaseAdminEmailHandler):

    def send_mail(self, subject, message, *args, **kwargs):
        report_error_task.delay(subject, message, *args, **kwargs)


class AdminEmailScheduledHandler(BaseAdminEmailHandler):

    def send_mail(self, subject, message, *args, **kwargs):
        register_error_for_admin.delay(subject, message, *args, **kwargs)
