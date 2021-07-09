from flask_socketio import SocketIO

socketio = SocketIO(ping_interval=5, ping_timeout=120, async_mode="gevent")


def init_app(app):
    socketio.init_app(app)
