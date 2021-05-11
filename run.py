import os
from gevent import monkey

monkey.patch_all(subprocess=True)  # NOQA

from app import create_app, socketio


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
