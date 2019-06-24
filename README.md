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

### Minimal example

- Start the server and store the container id:

      $ SLURK_SERVER_ID=$(docker run -p 80:5000 -e SECRET_KEY=your-key -d slurk/server)

- Read the admin token from the logs:

      $ ADMIN_TOKEN=$(docker logs $SLURK_SERVER_ID 2> /dev/null | sed -n '/admin token:/{n;p;}')

- Generate a new token (``sed`` removes quotation from JSON-string):

      $ curl -X POST
             -H "Authorization: Token $ADMIN_TOKEN"
             -H "Content-Type: application/json"
             -H "Accept: application/json"
             -d '{"room": "test_room"}'
             localhost/api/v2/token | sed 's/^"\(.*\)"$/\1/'
      7dc2124e-f89f-4d06-9917-811df2a5bb89

- Visit http://localhost and use the token to log in.

Happy slurking!

[what's this]: https://clp-research.github.io/slurk/slurk_about.html#slurk-about
[Quickstart]: https://clp-research.github.io/slurk/slurk_quickstart.html#slurk-quickstart
[Installation]: https://clp-research.github.io/slurk/slurk_installation.html#slurk-installation
[flask]: http://flask.pocoo.org/
[flask-socketio]: https://flask-socketio.readthedocs.io/en/latest
