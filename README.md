Slurk - A Lightweight Chat Server for Dialogue Experiments and Data Collection
==============================================================================

Slurk (think “slack for mechanical turk”…) is a lightweight and easily extensible chat server built especially for conducting multimodal dialogue experiments or data collections. See [Slurk: What’s this?][what's this] for a description of the main concepts. Or jump right in with the [Quickstart] (after the [Installation], of course)!

Slurk is built in Python, on top of [flask] and [flask-socketio].

If you want to build the documentation yourself, you need the packages _sphinx_ and _sphinx_rtd_theme_. Then you can create the documentation in the _docs_ folder:

```
pip install sphinx sphinx_rtd_theme
cd docs
make html
```
The generated documentation can then be found at *docs/_build/*


Happy slurking!

[what's this]: https://dsg-bielefeld.github.io/slurk/slurk_about.html#slurk-about
[Quickstart]: https://dsg-bielefeld.github.io/slurk/slurk_quickstart.html#slurk-quickstart
[Installation]: https://dsg-bielefeld.github.io/slurk/slurk_installation.html#slurk-installation
[flask]: http://flask.pocoo.org/
[flask-socketio]: https://flask-socketio.readthedocs.io/en/latest
