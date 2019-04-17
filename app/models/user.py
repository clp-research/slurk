from .. import db, login_manager

from . import Base, user_room, current_user_room

from .token import Token


class User(Base):
    __tablename__ = 'User'

    name = db.Column(db.String)
    token = db.relationship("Token", backref="user", uselist=False)
    rooms = db.relationship("Room", secondary=user_room, back_populates="users", lazy='dynamic')
    current_rooms = db.relationship("Room", secondary=current_user_room, back_populates="current_users", lazy='dynamic')
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
        try:
            token = Token.query.get(token_id)
        except:
            return None
    if not token:
        token_id = request.args.get('token')
        if token_id:
            token = Token.query.get(token_id)

    if token and token.valid:
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
