========
seedling
========

Watering and temperature control system for seed germination

License: MIT

Basic Commands
--------------

Type checks
^^^^^^^^^^^

Running type checks with mypy::

    $ mypy seedling

Test coverage
^^^^^^^^^^^^^

To run the tests, check your test coverage, and generate an HTML coverage report::

    $ coverage run -m pytest
    $ coverage html
    $ open htmlcov/index.html

Running tests with pytest::

    $ pytest

Live reloading and Sass CSS compilation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Moved to [Live reloading and SASS compilation](https://cookiecutter-django.readthedocs.io/en/latest/developing-locally.html#sass-compilation-live-reloading).

Systemd
--------

Copy files to ``/etc/systemd/system/``. Ensure that the directory ``home/pi/Logs/seedling/`` exists.

List all services::

    systemctl list-unit-files --type=service

Start service::

    systemctl start server


Check service status::

    systemctl status server




Hardware Notes
--------------

Raspberry Pi 5 Model B Rev 1.1
