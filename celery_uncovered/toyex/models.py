class Repository(object):
    def __init__(self, obj):
        self._wrapped_obj = obj
        self.language = obj[u'language'] or u'unknown'
        self.name = obj[u'full_name']

    def __getattr__(self, attr):
        if attr in self.__dict__:
            return getattr(self, attr)
        else:
            return getattr(self._wrapped_obj, attr)


class ErrorRecord(object):
    """docstring for ErrorRecord"""
    def __init__(self, subject, message):
        self.subject = subject
        self.message = message
