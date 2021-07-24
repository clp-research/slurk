[![Lint Status](https://github.com/clp-research/slurk/actions/workflows/lint.yml/badge.svg?branch=master)](https://github.com/clp-research/slurk/actions/workflows/lint.yml)
[![Test Status](https://github.com/clp-research/slurk/actions/workflows/test.yml/badge.svg?branch=master)](https://github.com/clp-research/slurk/actions/workflows/test.yml)
[![Documentation Status](https://github.com/clp-research/slurk/actions/workflows/docs.yml/badge.svg?branch=master)](https://github.com/clp-research/slurk/actions/workflows/docs.yml)
[![Docker Cloud Automated build](https://img.shields.io/docker/cloud/automated/slurk/server)](https://hub.docker.com/r/slurk/server)

Slurk - A Lightweight Chat Server for Dialogue Experiments and Data Collection
==============================================================================

Slurk (think "slack for mechanical turk"...) is a lightweight and easily extensible chat server built especially for
conducting multimodal dialogue experiments or data collections. See [Slurk: What’s this?][what's this] for a description
of the main concepts. Or jump right in with the [Getting Started][] Guide!

The main idea of Slurk is to have a platform that can be used without any change to the Slurk Server
by creating task-specific bots. The bots can create rooms, custom chat layouts, and control
the distribution of users to rooms. In the following architecture overview, the main
components of Slurk are outlined.

![Slurk architecture][architecture]

Slurk is built in Python 3.9, on top of [Flask] and [Flask-SocketIO].

To run slurk, the simplest way is to use docker

```bash
$ docker run -p 80:80 -e SLURK_DATABASE_URI=sqlite:////slurk.db slurk/server
admin token:
01234567-89ab-cdef-0123-456789abcdef
```

Now you can open `localhost` in your browser and log in with any username and the provided admin token


The [full documentation][doc] can be found on GitHUb.

Happy slurking!

[what's this]: https://clp-research.github.io/slurk/slurk_about.html#slurk-about
[Getting Started]: https://clp-research.github.io/slurk/slurk_gettingstarted.html
[Installation]: https://clp-research.github.io/slurk/slurk_installation.html#slurk-installation
[Flask]: http://flask.pocoo.org/
[Flask-SocketIO]: https://flask-socketio.readthedocs.io/en/latest
[architecture]: docs/slurk_architecture.png
[doc]: https://clp-research.github.io/slurk/
