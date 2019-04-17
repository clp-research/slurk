from flask_login import current_user

from .. import socketio

from ..models.user import User


@socketio.on('get_permissions_by_user')
def _get_permissions_by_user(id):
    if not current_user.get_id():
        return False, "invalid session id"
    if id and not current_user.token.permissions.permissions_query:
        return False, "insufficient rights"

    if id:
        user = User.query.get(id)
    else:
        user = current_user

    if user:
        return True, user.token.permissions.as_dict()
    else:
        return False, "user does not exist"
