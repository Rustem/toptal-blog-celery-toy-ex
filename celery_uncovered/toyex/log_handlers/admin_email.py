from django.utils.log import AdminEmailHandler as BaseAdminEmailHandler
from celery_uncovered.toyex.tasks import report_error_task, create_error_file


class AdminEmailHandler(BaseAdminEmailHandler):

    def send_mail(self, subject, message, *args, **kwargs):
        report_error_task.delay(subject, message, *args, **kwargs)


class AdminEmailScheduledHandler(BaseAdminEmailHandler):

    def send_mail(self, subject, message, *args, **kwargs):
        print("safdsdfasdfasd")
        create_error_file.delay(subject, message, *args, **kwargs)
