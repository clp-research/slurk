from flask_login import current_user
from flask import request

from .. import db, socketio

from . import user_room
from .token import Token
from .layout import Layout
from .user import User


class Room(db.Model):
    __tablename__ = 'Room'

    name = db.Column(db.String, primary_key=True)
    label = db.Column(db.String, nullable=False)
    layout_id = db.Column(db.Integer, db.ForeignKey(Layout.id))
    read_only = db.Column(db.Boolean, default=False, nullable=False)
    show_users = db.Column(db.Boolean, default=True, nullable=False)
    show_latency = db.Column(db.Boolean, default=True, nullable=False)
    show_input = db.Column(db.Boolean, default=True, nullable=False)
    show_history = db.Column(db.Boolean, default=True, nullable=False)
    show_interaction_Area = db.Column(db.Boolean, default=True, nullable=False)
    static = db.Column(db.Boolean, default=False, nullable=False)
    tokens = db.relationship(Token, backref="room")
    users = db.relationship("User", secondary=user_room, back_populates="rooms")

    def __repr__(self):
        return "<Room(name='%s', label='%s', layout='%s')>" % (self.name, self.label, self.layout.name)

    def as_dict(self):
        return {
            'name': self.name,
            'label': self.label,
            'layout': self.layout.id,
            'read_only': self.read_only,
            'show_users': self.show_users,
            'show_latency': self.show_latency,
            'show_input': self.show_input,
            'show_history': self.show_history,
            'show_interaction_Area': self.show_interaction_Area,
            'static': self.static,
            'users': {user.id: user.as_dict() for user in self.users},
        }


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


@socketio.on('get_room')
def _get_room(name):
    if not current_user.get_id():
        return False, "invalid session id"
    if not current_user.token.permissions.query_room:
        return False, "insufficient rights"
    room = Room.query.get(name)
    if room:
        return True, room.as_dict()
    else:
        return False, "room does not exist"
