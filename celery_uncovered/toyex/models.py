class Repository(object):

    UNKNOWN_LANG = 'unknown'

    def __init__(self, obj):
        self._wrapped_obj = obj
        self.name = obj[u'full_name']
        self.language = obj[u'language'] or self.UNKNOWN_LANG

    def __getattr__(self, attr):
        if attr in self.__dict__:
            return getattr(self, attr)
        else:
            return getattr(self._wrapped_obj, attr)
