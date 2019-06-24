from flask_login import current_user
from sqlalchemy.exc import IntegrityError

from .. import socketio, db

from ..models.token import Token


@socketio.on('get_token')
def _get_token(id):
    if not current_user.get_id():
        return False, "invalid session id"
    if not current_user.token.permissions.token_query:
        return False, "insufficient rights"
    token = Token.query.get(id)
    if token:
        return True, token.as_dict()
    else:
        return False, "token does not exist"


@socketio.on('invalidate_token')
def _invalidate_token(id):
    if not current_user.get_id():
        return False, "invalid session id"
    if not current_user.token.permissions.token_invalidate:
        return False, "insufficient rights"
    token = Token.query.get(id)
    if token:
        was_valid = token.valid
        token.valid = False
        db.session.commit()
        return True, was_valid
    else:
        return False, "token does not exist"


@socketio.on('remove_token')
def _remove_token(id):
    if not current_user.get_id():
        return False, "invalid session id"
    if not current_user.token.permissions.token_remove:
        return False, "insufficient rights"

    try:
        deleted = Token.query.filter_by(id=id).delete()
        db.session.commit()
        return True, bool(deleted)
    except IntegrityError as e:
        return False, str(e)
