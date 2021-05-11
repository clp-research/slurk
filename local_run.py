import os
from gevent import monkey

monkey.patch_all(subprocess=True)  # NOQA

from app import create_app, socketio

os.environ["SECRET_KEY"] = "TEST"
os.environ["DEBUG"] = "True"
basedir = os.path.abspath(os.path.dirname(__file__))
os.environ["DATABASE"] = f"sqlite:///{os.path.join(basedir, 'slurk.db')}"

if __name__ == '__main__':
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))

    app = create_app()
    socketio.run(
        app,
        host,
        port,
        extra_files=[
            "app/templates",
            "app/static/js",
            "app/static/css",
            "app/static/layouts"])
