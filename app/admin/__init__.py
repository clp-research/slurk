from flask import Blueprint, render_template, request
from flask_login import login_required

from .. import db

from ..models.room import Room
from ..models.task import Task
from ..models.token import Token
from ..models.permission import Permissions

from .forms import TokenGenerationForm, TaskGenerationForm

admin = Blueprint('admin', __name__, url_prefix="/admin")


def _to_bool(var):
    return var.lower() not in ("f", "false", "0", "no", "off")


def _boolean_parameter(name, default=False):
    parameter = request.args.get(name, None) if request.method == 'GET' else None
    if parameter:
        return _to_bool(parameter)
    else:
        return default


def _int_parameter(name, default=None):
    parameter = request.args.get(name, None) if request.method == 'GET' else None
    if parameter:
        return int(parameter)
    else:
        return default


def _string_parameter(name, default=None):
    parameter = request.args.get(name, None) if request.method == 'GET' else None
    if parameter:
        return parameter
    else:
        return default


@admin.route('/token', methods=['GET', 'POST'])
@login_required
def token():
    form = TokenGenerationForm(
        source=_string_parameter("source"),
        room=_string_parameter("room"),
        task=_int_parameter("task", 0),
        count=_int_parameter("count", 1),
        user_query=_boolean_parameter("user_query"),
        user_permissions_query=_boolean_parameter("user_permissions_query"),
        user_permissions_update=_boolean_parameter("user_permissions_update"),
        user_room_query=_boolean_parameter("user_room_query"),
        user_room_join=_boolean_parameter("user_room_join"),
        user_room_leave=_boolean_parameter("user_room_leave"),
        message_text=_boolean_parameter("message_text"),
        message_image=_boolean_parameter("message_image"),
        message_command=_boolean_parameter("message_command"),
        message_history=_boolean_parameter("message_history"),
        message_broadcast=_boolean_parameter("message_broadcast"),
        room_query=_boolean_parameter("room_query"),
        room_create=_boolean_parameter("room_create"),
        room_close=_boolean_parameter("room_close"),
        layout_query=_boolean_parameter("layout_query"),
        task_create=_boolean_parameter("task_create"),
        task_query=_boolean_parameter("task_query"),
        token_generate=_boolean_parameter("token_generate"),
        token_query=_boolean_parameter("token_query"),
        token_invalidate=_boolean_parameter("token_invalidate"),
        token_remove=_boolean_parameter("token_remove"),
    )

    room = Room.query.get(form.room.data)
    task = db.session.query(Task).filter_by(id=form.task.data).first()

    if not room:
        form.room.choices = [(room.name, room.label) for room in db.session.query(Room).filter_by(static=True).all()]
        form.task.choices = [(task.id, task.name) for task in db.session.query(Task).all()]
        form.task.choices.insert(0, (-1, 'None'))
        return render_template('token.html', form=form, title="Token generation")

    tokens = [Token(source=form.source.data,
                    room=room,
                    task=task,
                    permissions=Permissions(
                        user_query=form.user_query.data,
                        user_permissions_query=form.user_permissions_query.data,
                        user_permissions_update=form.user_permissions_update.data,
                        user_room_join=form.user_room_join.data,
                        user_room_query=form.user_room_query.data,
                        user_room_leave=form.user_room_leave.data,
                        message_text=form.message_text.data,
                        message_image=form.message_image.data,
                        message_command=form.message_command.data,
                        message_history=form.message_history.data,
                        message_broadcast=form.message_broadcast.data,
                        room_query=form.room_query.data,
                        room_create=form.room_create.data,
                        room_close=form.room_close.data,
                        layout_query=form.layout_query.data,
                        task_create=form.task_create.data,
                        task_query=form.task_create.data,
                        token_generate=form.token_generate.data,
                        token_query=form.token_query.data,
                        token_invalidate=form.token_invalidate.data,
                        token_remove=form.token_remove.data,
                    ))
              for _ in range(0, form.count.data or 1)]
    db.session.add_all(tokens)
    db.session.commit()
    return "<br>".join([str(tk.id) for tk in tokens])


@admin.route('/task', methods=['GET', 'POST'])
@login_required
def task():
    form = TaskGenerationForm(
        name=_string_parameter("name"),
        num_users=_int_parameter("num"),
    )

    name = form.name.data
    num_users = form.num_users.data

    if not name or not num_users:
        return render_template('task.html', form=form, title="Task generation")

    db.session.add(Task(name=name, num_users=num_users))
    db.session.commit()
    return f"Task \"{name}\" created"
