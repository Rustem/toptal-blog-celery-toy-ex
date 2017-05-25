from celery import current_app
from celery.utils.log import get_task_logger
from django.conf import settings
from .models import get_current_scenario


DEFAULT_SCENARIO_ID = getattr(settings, 'DEFAULT_SCENARIO_ID', 1)


class LoggingTask(current_app.Task):
    abstract = True
    ignore_result = False

    @property
    def log(self):
        logger = get_task_logger(self.name)
        return logger

    def log_msg(self, msg, *msg_args):
        self.log.debug(msg, *msg_args)


class ScopeBasedTask(current_app.Task):
    abstract = True
    ignore_result = False
    default_scenario_id = DEFAULT_SCENARIO_ID
    scope_args = ('scenario_id',)

    def __init__(self, *args, **kwargs):
        super(ScopeBasedTask, self).__init__(*args, **kwargs)
        self.set_scenario(scenario_id=kwargs.get('scenario_id', None))

    def set_scenario(self, scenario_id=None):
        self.scenario_id = self.default_scenario_id
        if scenario_id:
            self.scenario_id = scenario_id
        else:
            self.scenario_id = get_current_scenario().id

    def apply_async(self, args=None, kwargs=None, **other_kwargs):
        self.inject_scope_args(kwargs)
        return super(ScopeBasedTask, self).apply_async(args=args, kwargs=kwargs, **other_kwargs)

    def __call__(self, *args, **kwargs):
        task_rv = super(ScopeBasedTask, self).__call__(*args, **kwargs)
        return task_rv

    def signature(self, args=None, *starargs, **starkwargs):
        """
        def sig(args=None, *starargs, **starkwargs):

            print args
            print starargs
            print starkwargs

        sig(args=1, *(1,2,3), **{}) - violates
        sig(args=1, *(1,2,3), **{'args': (1, 2, 3)}) - violates
        sig(args=1, *(), **{}) - possible
        sig(1, *(1, 2, 3), **{}) - possible

        .sig
            signature(args, kwargs)
            signature(args=None, kwargs=None)
        """
        # WARN reconcialiate args, kwargs with celery
        if len(starargs) == 0:
            starargs = args
            kwargs = starkwargs.setdefault('kwargs', {})
            self.set_scenario(scenario_id=kwargs.get('scenario_id', None))
            self.inject_scope_args(kwargs)
            return super(ScopeBasedTask, self).signature(args=args, **starkwargs)
        else:
            self.set_scenario(scenario_id=starargs[0].get('scenario_id', None))
            self.inject_scope_args(starargs[0])
            # starargs[0].update(starkwargs)
            self.log_msg("SIGNATURE called with args=%s, starargs=%s, starkwargs=%s", list(args), list(starargs), starkwargs)
            return super(ScopeBasedTask, self).signature(args, *starargs, **starkwargs)

    subtask = signature

    def s(self, *a, **kw):
        """Create signature.

        Shortcut for ``.s(*a, **k) -> .signature(a, k)``.
        """
        return self.signature(a, kw)

    def si(self, *a, **kw):
        """Create immutable signature.

        Shortcut for ``.si(*a, **k) -> .signature(a, k, immutable=True)``.
        """
        return self.signature(a, kw, immutable=True)

    def inject_scope_args(self, kwargs):
        for arg in self.scope_args:
            if arg not in kwargs:
                kwargs[arg] = getattr(self, arg)
