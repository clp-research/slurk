from flask import Blueprint, render_template, request

from .. import db, settings

from ..models.room import Room
from ..models.task import Task
from ..models.token import Token
from ..models.permission import Permissions

from .forms import TokenGenerationForm

admin = Blueprint('admin', __name__, url_prefix="/admin")


def _to_bool(var):
    return var.lower() not in ("f", "false", "0", "no", "off")


@admin.route('/token', methods=['GET', 'POST'])
def token():
    source = request.args.get("source", None) if request.method == 'GET' else None
    room = request.args.get("room", None) if request.method == 'GET' else None
    task = request.args.get("task", None) if request.method == 'GET' else None
    if task:
        task = int(task)
    count = request.args.get("count", None) if request.method == 'GET' else None
    if count:
        count = int(count)
    query_user = request.args.get("query_user", None) if request.method == 'GET' else None
    if query_user:
        query_user = _to_bool(query_user)
    query_permissions = request.args.get("query_permissions", None) if request.method == 'GET' else None
    if query_permissions:
        query_permissions = _to_bool(query_permissions)
    query_room = request.args.get("query_room", None) if request.method == 'GET' else None
    if query_room:
        query_room = _to_bool(query_room)
    message_send = request.args.get("message_send", None) if request.method == 'GET' else None
    if message_send:
        message_send = _to_bool(message_send)
    message_history = request.args.get("message_history", None) if request.method == 'GET' else None
    if message_history:
        message_history = _to_bool(message_history)
    message_broadcast = request.args.get("message_broadcast", None) if request.method == 'GET' else None
    if message_broadcast:
        message_broadcast = _to_bool(message_broadcast)
    key = request.args.get("key", None) if request.method == 'GET' else None

    form = TokenGenerationForm(task=task or 0, count=count or 1, source=source or "", key=key or "", room=room or 1)

    if form.is_submitted():
        source = form.source.data
        room = form.room.data
        task = form.task.data
        count = form.count.data
        key = form.key.data
        query_user = form.query_user.data
        query_room = form.query_room.data
        query_permissions = form.query_permissions.data
        message_send = form.message_send.data
        message_history = form.message_history.data
        message_broadcast = form.message_broadcast.data

    room = Room.query.get(room) if room else None
    task = db.session.query(Task).filter_by(id=task).first() or None

    if not room or not key:
        form.room.choices = [(room.name, room.label) for room in db.session.query(Room).filter_by(static=True).all()]
        form.task.choices = [(task.id, task.name) for task in db.session.query(Task).all()]
        form.task.choices.insert(0, (-1, 'None'))
        return render_template('token.html', form=form, title="Token generation")

    if key != settings.secret_key:
        return "Invalid password"

    source = source if source is not "" else None

    tokens = [Token(source=source,
                    room=room,
                    task=task,
                    permissions=Permissions(query_user=query_user,
                                            query_room=query_room,
                                            query_permissions=query_permissions,
                                            message_send=message_send,
                                            message_history=message_history,
                                            message_broadcast=message_broadcast))
              for _ in range(0, count or 1)]
    db.session.add_all(tokens)
    db.session.commit()
    return "<br >".join([str(tk.id) for tk in tokens])
