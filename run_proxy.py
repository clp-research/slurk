import os
from gevent import monkey
from werkzeug.middleware.proxy_fix import ProxyFix

monkey.patch_all(subprocess=True)

from app import app, socketio

if __name__ == '__main__':
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))

    app = ProxyFix(app, x_for=1, x_prefix=1)

    socketio.run(app, host, port,
                 extra_files=["app/templates", "app/static/js", "app/static/css", "app/static/layouts"])
