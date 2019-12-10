Slurk - A Lightweight Chat Server for Dialogue Experiments and Data Collection
==============================================================================

Slurk (think “slack for mechanical turk”…) is a lightweight and easily extensible chat server built especially for 
conducting multimodal dialogue experiments or data collections. See [Slurk: What’s this?][what's this] for a description 
of the main concepts. Or jump right in with the [Getting Started][] Guide!

The main idea of Slurk is to have a platform can be used without any change to the Slurk Server
by creating task-specific bots. The bots can create rooms, custom chat layouts and control
the distribution of users to rooms. In the following architecture overview the main
components of Slurk are outlined. 

![Slurk architecture][architecture]

Slurk is built in Python 3, on top of [flask] and [flask-socketio].

If you want to build the documentation yourself, you need the packages _sphinx_ and _sphinx_rtd_theme_. Then you can create the documentation in the _docs_ folder:

```
pip install sphinx sphinx_rtd_theme
cd docs
make html
```

The full documentation can then be found at *docs/_build/*

Happy slurking!

[what's this]: https://clp-research.github.io/slurk/slurk_about.html#slurk-about
[Getting Started]: https://clp-research.github.io/slurk/slurk_gettingstarted.html
[Installation]: https://clp-research.github.io/slurk/slurk_installation.html#slurk-installation
[flask]: http://flask.pocoo.org/
[flask-socketio]: https://flask-socketio.readthedocs.io/en/latest
[architecture]: img/slurk_architecture.png