from flask import request

from .. import db, socketio

from . import Base, user_room


class User(Base):
    __tablename__ = 'User'

    name = db.Column(db.String, nullable=False)
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

    def __repr__(self):
        return str(self.as_dict())


@socketio.on('get_user')
def _get_user(id):
    user = User.query.filter_by(session_id=request.sid).first()
    if not user:
        return False, "invalid session id"
    if id:
        if not user.token.permissions.query_user:
            return False, "insufficient rights"
        user = User.query.get(id)
    if user:
        return True, user.as_dict()
    else:
        return False, "user does not exist"
