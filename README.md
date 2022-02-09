[![Lint Status](https://github.com/clp-research/slurk/actions/workflows/lint.yml/badge.svg?branch=master)](https://github.com/clp-research/slurk/actions/workflows/lint.yml)
[![Test Status](https://github.com/clp-research/slurk/actions/workflows/test.yml/badge.svg?branch=master)](https://github.com/clp-research/slurk/actions/workflows/test.yml)
[![Documentation Status](https://github.com/clp-research/slurk/actions/workflows/docs.yml/badge.svg?branch=master)](https://github.com/clp-research/slurk/actions/workflows/docs.yml)
[![Docker Cloud Automated build](https://img.shields.io/docker/cloud/automated/slurk/server)](https://hub.docker.com/r/slurk/server)

Slurk - A Lightweight Chat Server for Dialogue Experiments and Data Collection
==============================================================================

Slurk (think "slack for mechanical turk"...) is a lightweight and easily extensible chat server built especially for
conducting multimodal dialogue experiments or data collections. See [Slurk: What’s this?][what's this] for a description
of the key concepts. Or jump right in with the [Getting Started][] Guide!

The main idea of Slurk is to have a platform that can be used with no change to the Slurk Server
by creating task-specific bots. The bots can create rooms, custom chat layouts, and control
the distribution of users to rooms. In the following architecture overview, the key
components of Slurk are outlined.

![Slurk architecture][architecture]

Slurk is built in Python 3.9, on top of [Flask] and [Flask-SocketIO].
The latest version lives on the master branch. Branch 2.0.0 holds an older version.

To run slurk, the simplest way is to use docker

```text
$ docker run -p 5000:80 slurk/server
[2021-07-24 10:49:41 +0000] [1] [INFO] Starting gunicorn 20.1.0
[2021-07-24 10:49:41 +0000] [1] [INFO] Listening at: http://0.0.0.0:80 (1)
[2021-07-24 10:49:41 +0000] [1] [INFO] Using worker: geventwebsocket.gunicorn.workers.GeventWebSocketWorker
[2021-07-24 10:49:41 +0000] [8] [INFO] Booting worker with pid: 8
[2021-07-24 10:49:42,779] WARNING in database: SQLite should not be used in production
admin token:
01234567-89ab-cdef-0123-456789abcdef
```

Now you may create a room and a token with the provided admin token, open `http://localhost:5000` in your browser, and log in. The [full documentation][doc] on GitHub contains a detailed step-by-step guide on how to proceed further.

Happy slurking!

[what's this]: https://clp-research.github.io/slurk/slurk_about.html#slurk-about
[Getting Started]: https://clp-research.github.io/slurk/slurk_gettingstarted.html
[Installation]: https://clp-research.github.io/slurk/slurk_installation.html#slurk-installation
[Flask]: http://flask.pocoo.org/
[Flask-SocketIO]: https://flask-socketio.readthedocs.io/en/latest
[architecture]: docs/slurk_architecture.png
[doc]: https://clp-research.github.io/slurk/
