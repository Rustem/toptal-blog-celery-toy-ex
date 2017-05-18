Celery Uncovered
================

Supporting project for my toptal article - URL

This repository is intended to help the beginners better understand celery by usecases. It also shows some really nice (undocumented) tricks that could give lots of benefits while developing celery-based projects.

.. image:: https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg
     :target: https://github.com/pydanny/cookiecutter-django/
     :alt: Built with Cookiecutter Django


:License: MIT



Django-Applications
------------

toyex
^^^^^

    contains widely used (simple) examples of using celery to solve background tasks

advanced
^^^^^^

    contains generic patterns of using celery to facilitate workflow execution and many others

celery_tricks
^^^^^^^

    contains generic examples of extending default ```celery.app.Task``` and some undocument tricks such as:
        - verbose logging
        - scope injection
        - freezing task



Basic Modules
--------------


Celery
^^^^^^

This app comes with Celery.

To run a celery worker:

.. code-block:: bash

    cd celery_uncovered
    celery -A celery_uncovered.taskapp worker -l info

Please note: For Celery's import magic to work, it is important *where* the celery commands are run. If you are in the same folder with *manage.py*, you should be right.


Email Server
^^^^^^^^^^^^

In development, it is often nice to be able to see emails that are being sent from your application. For that reason local SMTP server `MailHog`_ with a web interface is available as docker container.

.. _mailhog: https://github.com/mailhog/MailHog

Container mailhog will start automatically when you will run all docker containers.
Please check `cookiecutter-django Docker documentation`_ for more details how to start all containers.

With MailHog running, to view messages that are sent by your application, open your browser and go to ``http://127.0.0.1:8025``


Test coverage
^^^^^^^^^^^^^

To run the tests, check your test coverage, and generate an HTML coverage report::

    $ coverage run manage.py test
    $ coverage html
    $ open htmlcov/index.html


Running tests with py.test
~~~~~~~~~~~~~~~~~~~~~~~~~~

::

  $ py.test

Live reloading and Sass CSS compilation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Moved to `Live reloading and SASS compilation`_.

.. _`Live reloading and SASS compilation`: http://cookiecutter-django.readthedocs.io/en/latest/live-reloading-and-sass-compilation.html





Deployment
----------

The following details how to deploy this application.
