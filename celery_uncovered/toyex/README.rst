Running examples
----------------

Fetch Github Repositories Task
^^^^^^^^^^^^^^^^^^^^^

Uses Celery Groups for execute multiple requests to github and store report in CSV-file

In order to launch and check an actual behavior of the task, first start the Celery process:

.. code-block:: bash

    $ celery -A celery_uncovered worker -l info


Then you will be able to test functionality via Shell:

.. code-block:: python

    from celery_uncovered.toyex.tasks import produce_hot_repo_report
    produce_hot_repo_report('day')


Finally, to see the result, navigate to the `celery_uncovered/media` directory and open the corresponding log file called similar to `github-hot-repos-2017-08-29.csv`. You might see something similar as below after running this task multiple times:

.. code-block:: bash

    1C Enterprise,arkuznetsov/scenex
    ASP,carsio/Projeto-Unity
    ActionScript,nicothezulu/EveryplayANE
    Arduino,braindead1/WemosD1_HomeMatic_StatusDisplay
    ...


You also can test it by passing a kwarg `ref_date`. Task will fetch only repositories created after referred date:

.. code-block:: python

    from celery_uncovered.toyex.tasks import produce_hot_repo_report
    produce_hot_repo_report(None, '2017-08-30')


You will find the report in file called `github-hot-repos-2017-08-30.csv`.
