from celery import shared_task
from .celery_ext import LoggingTask, ScopeBasedTask
from .utils import read_fixture

r"""
Responsible: Rustem Kamun <xepa4ep>

Configure celery in order to support verbose file logging per each task.

Implementation details:

1. Extend base task so that it allows to write logs to corresponding file handler

2. Configure celery logging so that it will write output to file. Most approapriate way is to use `signals.celeryd_after_setup` hook.

3. Build dummy tasks that logs some messages, errors to the log file.

4. Test that std, err stream is written to corresponding task file

Bonus tasks:

1. Celery completely tracks lifecycle of a task, including stages run and failure stages. Could u refine the code so that it will log task failure and task success stages?

2. Default logging configuration keeps corresponding task files opened during main process lifecycle. However it is common for enterprise software to have logs that are not kept open and therefore able to be deleted. For example, when I want to delete /logs/*log files, it must recreate them by appending new information. Current configuration does not allow that. You need to modify current logging configuration to support the following scenario:
    * append to the logfile name with the new loginformation
    * close file and release its descriptor

Hint: Clue within appropriate log handlers.
"""


@shared_task(bind=True, base=LoggingTask)
def add(self, a, b):
    c = a + b
    self.log_msg("Result of %i + %i = %i", a, b, c)
    return c


r"""
Responsible: Rustem Kamun <xepa4ep>

Injecting scope to each scope-based task. Sometimes you need to maintain some global scope beyond one app process. For example, our application depends on scenario. Scenario locates family of tables (a table space) you want to access//modify. Scenarios has same structure, but different data. Say, we do some action in app process within scenario X. In turn this action triggers another action but execution will be offloaded to celery. Celery should encapsulate scope (in our case scenario X). There are two options to solve this problem:

1) Pass scenario_id as parameter directly
2) Injecting scope to each task that require it

Of course if you have only a few tasks you prefer option (1) due to its simplicity. However, when you deal with execution topology which is hierarchical, you wish to solve it with option (2), because it is higher-level, less buggy and cleaner approach.

Implementation details:

1. Extend base task so that it allows to inject current scope as `**kwargs`. For example, `scenario_id`=None

2. Test that scenario injected consistently on the following scenarios
    2.1 call via delay and apply_async
    2.3 call from app->celery
    2.4 call from celery->celery (nested call)

Bonus tasks

1. Currently u can't maintain consistent scenario passing when you call by signature. For example, u can't use celery.canvas utilities such as group, chain, chord. Modify it so that it will be possible to call it by signature and its aliases: subtask, signature, s, si. Modify also test suite to address this piece of functionality.

2. Allow this type of tasks to be loggable as well. You can reuse functionality of verbose logging trick.
"""


@shared_task(bind=True, base=ScopeBasedTask)
def read_scenario_file_task(self, **kwargs):
    fixture_parts = ["scenarios", "sc_%i.json" % kwargs['scenario_id']]
    self.log_msg("Called with scenario_id=%s", kwargs['scenario_id'])
    return read_fixture(*fixture_parts)

r"""
Responsible: Rustem Kamun <xepa4ep>
If you merely want to refer to the result of a previously executed task or you want to track task in external storage, then that is definitely possible by freezing task. The meaning of freezing is finalizing signature instance.

```task_result = task.freeze()```

Next example is probably not best example, however I can't share a real case where I used this because of the privacy.

Let's say you want to execute payment transaction via some payment broker. You don't want your user wait before actual transaction is accopmlished. You would rather want to show your user "Thank you" page and enqueue your payment tx. Tiny periodic `status_manager` observing [status=QUEUED] payments, marks them as PENDING. Tiny periodic `payment_dispatcher` tracks all PENDING tasks, registers them to `execute_payment_task`. So we don't want to execute PENDING tasks twice, so we are also assign to payment object exec_identifier as task uuid. Here we use freezing.



Implementation details:

1. Define Payment object as simple as possible with status=[QUEUED, PENDING, SETTLED, DECLINED]

2. Tiny status manager which is responsible to prepare queued to pending

3. Tiny payment dispatcher which is responsible for assigning PENDING to execute_payment task and set exec identifier so that it will be executed only once.


Bonus tasks:

1. freeze to access task result in indirect parent.

a = A.s()
a_result = a.freeze()

workflow = (a | B.s() | C.s(a_result.as_tuple()))
workflow.delay()

https://github.com/celery/celery/issues/3666
"""
