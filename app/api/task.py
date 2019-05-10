from flask_login import current_user

from .. import socketio

from ..models.task import Task


@socketio.on('get_task')
def _get_task(id):
    if not current_user.get_id():
        return False, "invalid session id"
    if not current_user.token.permissions.task_query:
        return False, "insufficient rights"
    task = Task.query.get(id)
    if task:
        return True, task.as_dict()
    else:
        return False, "task does not exist"
