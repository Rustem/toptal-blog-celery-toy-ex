Running examples
----------------

File Logging Per Task
^^^^^^^^^^^^^^^^^^^^^

Extend Celery so that each task logs its standard output and errors to files

In order to launch and test how this task is working, first start the Celery process:

.. code-block:: bash

    $ celery -A celery_uncovered worker -l info


Then you will be able to test functionality via Shell:

.. code-block:: python

    from datetime import date
    from celery_uncovered.tricks.tasks import add
    add.delay(1, 3)


Finally, to see the result, navigate to the `celery_uncovered/logs` directory and open the corresponding log file called `celery_uncovered.tricks.tasks.add.log`. You might see something similar as below after running this task multiple times:

.. code-block:: bash

    Result of 1 + 2 = 3
    Result of 1 + 2 = 3
    ...


Scope-Aware Tasks
^^^^^^^^^^^^^^^^^^^^^

Automatically inherit scope from one execution context and inject it into the current execution context as a parameter.
    
First start the Celery process:

.. code-block:: bash

    $ celery -A celery_uncovered worker -l info


Import and execute a dummy task from celery_uncovered/tricks/tasks.py:

.. code-block:: python

    from celery_uncovered.tricks.tasks import read_scenario_file_task
    read_scenario_file_task.delay(scenario_id=2).get()


You will see the following result

.. code-block:: python
    
    Out[3]: {u'name': u'B'}


You also can test it without passing a kwarg `scenario_id`. Celery implicitly will use activated scenario:

.. code-block:: python

    from celery_uncovered.tricks.tasks import read_scenario_file_task
    read_scenario_file_task.delay(scenario_id=2).get()


You will see the following result

.. code-block:: python

    Out[4]: {u'name': u'A'}

