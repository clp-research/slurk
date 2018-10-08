.. _slurk_installation:

=========================================
Installation
=========================================

You will need Python 3.6+ and `pip`. To test the dialogue setup, you will also need to have two different web browsers on your system.

To install the requirements and prepare for testing, do the following. (We assume that you have cloned the repository.)

- Set up a virtual environment, if you like. (Optional.) E.g. with `virtualenv`:

  - ``virtualenv -p /usr/bin/python3.6 slurk_test``
  - ``source my_virtualenv/bin/activate``

- Install the requirements:

  - ``pip install -r requirements.txt``

- Prepare the directory:

  - make a copy of ``config.template.ini``, name it ``config.ini``
  - adjust ``host``, ``port`` and ``ssl`` in ``config.ini``, or leave it at defaults (which is to use `localhost:5000` and no encryption).
  - If you have tested this before and are getting an error, try ``rm -rf botsi.db``.
