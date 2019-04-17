from flask_login import current_user

from .. import socketio

from ..models.layout import Layout
from ..models.user import User


@socketio.on('get_layout')
def _get_layout(id):
    if not current_user.get_id():
        return False, "invalid session id"
    if not current_user.token.permissions.layout_query:
        return False, "insufficient rights"
    layout = Layout.query.get(id)
    if layout:
        return True, layout.as_dict()
    else:
        return False, "layout does not exist"


@socketio.on('get_layouts_by_user')
def _get_layouts_by_user(id):
    if not current_user.get_id():
        return False, "invalid session id"

    if id:
        if not current_user.token.permissions.layout_query:
            return False, "insufficient rights"
        user = User.query.get(id)
    else:
        user = current_user

    if user:
        return True, {room.name: room.layout.as_dict() for room in user.rooms}
    else:
        return False, "user does not exist"
