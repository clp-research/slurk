from flask import request
from flask_login import current_user

from .. import db, socketio, login_manager

from . import Base, user_room

from .token import Token


class User(Base):
    __tablename__ = 'User'

    name = db.Column(db.String)
    token = db.relationship("Token", backref="user", uselist=False)
    rooms = db.relationship("Room", secondary=user_room, back_populates="users", lazy='dynamic')
    session_id = db.Column(db.String, unique=True)

    @property
    def is_active(self):
        return True

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def as_dict(self):
        return dict({
            'name': self.name,
            'token': str(self.token.id),
            'rooms': [room.name for room in self.rooms],
            'session_id': self.session_id,
        }, **super(User, self).as_dict())

    def get_id(self):
        return self.id


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


@login_manager.request_loader
def load_user_from_request(request):
    token = None
    token_id = request.headers.get('Authorization')
    if token_id:
        token = Token.query.get(token_id)
    if not token:
        token_id = request.args.get('token')
        if token_id:
            token = Token.query.get(token_id)

    if token:
        if not token.user:
            name = request.headers.get('Name')
            if not name:
                name = request.args.get('header')
            if not name:
                return None
            token.user = User(name=name)
            db.session.commit()
        return token.user
    return None


@socketio.on('get_rooms_by_user')
def _get_rooms_by_user(id):
    if not current_user.get_id():
        return False, "invalid session id"
    if id and not (current_user.token.permissions.query_room and current_user.token.permissions.query_user):
        return False, "insufficient rights"

    if id:
        user = User.query.get(id)
    else:
        user = current_user

    if user:
        return True, [room.as_dict() for room in user.rooms]
    else:
        return False, "user does not exist"


@socketio.on('get_permissions_by_user')
def _get_permissions_by_user(id):
    if not current_user.get_id():
        return False, "invalid session id"
    if id and not (current_user.token.permissions.query_permissions and current_user.token.permissions.query_user):
        return False, "insufficient rights"

    if id:
        user = User.query.get(id)
    else:
        user = current_user

    if user:
        return True, user.token.permissions.as_dict()
    else:
        return False, "user does not exist"


@socketio.on('get_layouts_by_user')
def _get_layouts_by_user(id):
    if not current_user.get_id():
        return False, "invalid session id"

    if id:
        if not (current_user.token.permissions.query_layout and
                current_user.token.permissions.query_room and
                current_user.token.permissions.query_user):
            return False, "insufficient rights"
        user = User.query.get(id)
    else:
        user = current_user

    if user:
        return True, {room.name: room.layout.as_dict() for room in user.rooms}
    else:
        return False, "user does not exist"


@socketio.on('get_user')
def _get_user(id):
    current_id = current_user.get_id()
    if not current_id:
        return False, "invalid session id"

    if id and not current_user.token.permissions.query_user:
        return False, "insufficient rights"
    user = User.query.get(id or current_id)
    if user:
        return True, user.as_dict()
    else:
        return False, "user does not exist"
