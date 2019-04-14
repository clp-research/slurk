from flask import Flask, g
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_socketio import SocketIO

from .settings import Settings

socketio = SocketIO(ping_interval=5, ping_timeout=120, async_mode="gevent")

app = Flask(__name__)
app.config.from_object('config')

db = SQLAlchemy(app)
settings = Settings.from_object('config')
login_manager = LoginManager()

from .login import login as login_blueprint
from .admin import admin as admin_blueprint
from .chat import chat as chat_blueprint
app.register_blueprint(login_blueprint)
app.register_blueprint(admin_blueprint)
app.register_blueprint(chat_blueprint)

db.drop_all()
db.create_all()
login_manager.init_app(app)
login_manager.login_view = 'login.index'
socketio.init_app(app)


@login_manager.user_loader
def load_user(id):
    from .models.user import User
    return User.query.get(int(id))


@app.before_request
def before_request():
    g.user = current_user


from .models.room import Room
from .models.layout import Layout

if not Room.query.get("test_room"):
    db.session.add(Room(name="test_room",
                        label="Test Room",
                        static=True,
                        layout=Layout.from_json_file("test_room")))
db.session.commit()
