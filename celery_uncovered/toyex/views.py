from django.views.generic import View


class ReportErrorView(View):

    def get(self, request, *args, **kwargs):
        return 1 / 0
