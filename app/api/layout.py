from flask_login import current_user

from .. import socketio

from ..models.layout import Layout


def get_layout(id):
    return Layout.query.get(id)


@socketio.on('get_layout')
def _get_layout(id):
    if not current_user.get_id():
        return False, "invalid session id"
    if not current_user.token.permissions.layout_query:
        return False, "insufficient rights"

    layout = get_layout(id)

    if layout:
        return True, layout.as_dict()
    else:
        return False, "layout does not exist"
