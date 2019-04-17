from flask_login import current_user
from sqlalchemy.exc import IntegrityError

from .. import db, socketio

from . import user_room, current_user_room
from .token import Token
from .layout import Layout


class Room(db.Model):
    __tablename__ = 'Room'

    name = db.Column(db.String, primary_key=True)
    label = db.Column(db.String, nullable=False)
    layout_id = db.Column(db.Integer, db.ForeignKey(Layout.id))
    read_only = db.Column(db.Boolean, default=False, nullable=False)
    show_users = db.Column(db.Boolean, default=True, nullable=False)
    show_latency = db.Column(db.Boolean, default=True, nullable=False)
    static = db.Column(db.Boolean, default=False, nullable=False)
    tokens = db.relationship(Token, backref="room")
    users = db.relationship("User", secondary=user_room, back_populates="rooms")
    current_users = db.relationship("User", secondary=current_user_room, back_populates="current_rooms")

    def as_dict(self):
        return {
            'name': self.name,
            'label': self.label,
            'layout': self.layout_id,
            'read_only': self.read_only,
            'show_users': self.show_users,
            'show_latency': self.show_latency,
            'static': self.static,
            'users': {user.id: user.name for user in self.users},
            'current_users': {user.id: user.name for user in self.current_users},
        }


@socketio.on('get_room')
def _get_room(name):
    if not current_user.get_id():
        return False, "invalid session id"
    if not current_user.token.permissions.room_query:
        return False, "insufficient rights"
    room = Room.query.get(name)
    if room:
        return True, room.as_dict()
    else:
        return False, "room does not exist"


@socketio.on('create_room')
def _create_room(payload):
    if not current_user.get_id():
        return False, "invalid session id"
    if not current_user.token.permissions.room_create:
        return False, "insufficient rights"

    if 'name' not in payload:
        return False, 'missing argument: "name"'
    if 'label' not in payload:
        return False, 'missing argument: "label"'

    room = Room(
        name=payload['name'],
        label=payload['label'],
        layout_id=payload['layout'] if 'layout' in payload else None,
        read_only=payload['read_only'] if 'read_only' in payload else None,
        show_users=payload['show_users'] if 'show_users' in payload else None,
        show_latency=payload['show_latency'] if 'show_latency' in payload else None,
        static=payload['static'] if 'static' in payload else None,
    )
    db.session.add(room)
    try:
        db.session.commit()
        return True, room.as_dict()
    except IntegrityError as e:
        return False, str(e)


@socketio.on('delete_room')
def _delete_room(name):
    if not current_user.get_id():
        return False, "invalid session id"
    if not current_user.token.permissions.room_delete:
        return False, "insufficient rights"

    try:
        deleted = Room.query.filter_by(name=name).delete()
        db.session.commit()
        return True, bool(deleted)
    except IntegrityError as e:
        return False, str(e)
