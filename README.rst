Celery Uncovered
================

Supporting project for my `TopTal article`_.

.. _`TopTal article`: https://www.toptal.com/python/orchestrating-celery-python-background-jobs

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

advex
^^^^^^

    contains generic patterns of using celery to facilitate workflow execution and many others (soon)

`tricks`_
^^^^^^^

    contains generic examples of extending default ```celery.app.Task``` and some undocument tricks such as:
        - verbose logging
        - scope injection
        - freezing task

.. _tricks: https://github.com/Rustem/toptal-blog-celery-toy-ex/tree/master/celery_uncovered/tricks#running-examples


Extra Details
--------------


Celery
^^^^^^

This app comes with Celery.

To run a celery worker:

.. code-block:: bash

    cd celery_uncovered
    celery -A celery_uncovered worker -l info

Please note: For Celery's import magic to work, it is important *where* the celery commands are run. If you are in the same folder with *manage.py*, you should be right.


Email Server
^^^^^^^^^^^^

In development, it is often nice to be able to see emails that are being sent from your application. For that reason local SMTP server `MailHog`_ with a web interface is available as docker container.


With MailHog running, to view messages that are sent by your application, open your browser and go to ``http://127.0.0.1:8025``

How to deploy and run it via docker you can refer to its [README.md](docker/mailhog/README.md).

Further configuration options are available in `MailHog`_.

.. _mailhog: https://github.com/mailhog/MailHog


Running tests with py.test
~~~~~~~~~~~~~~~~~~~~~~~~~~

::

  $ chmod +x utility/unittest.sh
  $ ./utility/unittest.sh


Live reloading and Sass CSS compilation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Moved to `Live reloading and SASS compilation`_.

.. _`Live reloading and SASS compilation`: http://cookiecutter-django.readthedocs.io/en/latest/live-reloading-and-sass-compilation.html





Deployment
----------

The following details how to deploy this application.

Credits
------

  - Original Project
    * `Sattar Stamkulov`_
      contributed example

    * `Mailubayev Yernar`_
      contributed example

:: _`Sattar Stamkulov`: https://github.com/devishot
:: _`Mailubayev Yernar`: https://github.com/Mafioso
