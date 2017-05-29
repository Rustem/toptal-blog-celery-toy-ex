from django.conf import settings


DEFAULT_SCENARIO_ID = getattr(settings, 'DEFAULT_SCENARIO_ID')


class Scenario(object):

    def __init__(self, id, name='unknown'):
        self.id = id
        self.name = name

    @classmethod
    def default(cls):
        return Scenario(DEFAULT_SCENARIO_ID)


class ContextStack(object):

    def __init__(self):
        self.st = []

    def current(self):
        return self.st[0]

    def push(self, obj):
        self.st.insert(0, obj)

    def pop(self):
        if len(self.st) == 1:
            return self.current
        return self.st.pop(0)


class ScenarioContextStack(ContextStack):

    def __init__(self):
        super(ScenarioContextStack, self).__init__()
        self.push(Scenario.default())

    def pop_(self):
        if len(self.st) == 1:
            return self.current
        return self.st.pop(0)


context_stack = ScenarioContextStack()


def get_current_scenario():
    return context_stack.current()
