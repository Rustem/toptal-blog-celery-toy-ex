from django.utils.log import AdminEmailHandler
from ..tasks import report_error_task


class ToyexAdminEmailHandler(AdminEmailHandler):

    def __init__(self, include_html=False, email_backend=None):
        super(ToyexAdminEmailHandler, self).__init__(include_html, email_backend)

    def send_mail(self, subject, message, *args, **kwargs):
        print("asdasdasdasdasdsdasd")
        report_error_task.delay(subject, message, *args, **kwargs)
