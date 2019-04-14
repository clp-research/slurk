import os
from gevent import monkey

from app import app, socketio


monkey.patch_all(subprocess=True)

if __name__ == '__main__':
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))

    socketio.run(app, host, port)
