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
def token():
    form = TokenGenerationForm(source=_string_parameter("source"),
                               room=_string_parameter("room"),
                               task=_int_parameter("task", 0),
                               count=_int_parameter("count", 1),
                               query_user=_boolean_parameter("query_user"),
                               query_permissions=_boolean_parameter("query_permissions"),
                               query_room=_boolean_parameter("query_room"),
                               query_layout=_boolean_parameter("query_layout"),
                               message_text=_boolean_parameter("message_text"),
                               message_image=_boolean_parameter("message_image"),
                               message_command=_boolean_parameter("message_command"),
                               message_history=_boolean_parameter("message_history"),
                               message_broadcast=_boolean_parameter("message_broadcast"),    
                               token_generate=_boolean_parameter("token_generate"),
                               token_invalidate=_boolean_parameter("token_invalidate"),
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
                    permissions=Permissions(query_user=form.query_user.data,
                                            query_room=form.query_room.data,
                                            query_permissions=form.query_permissions.data,
                                            query_layout=form.query_layout.data,
                                            message_text=form.message_text.data,
                                            message_image=form.message_image.data,
                                            message_command=form.message_command.data,
                                            message_history=form.message_history.data,
                                            message_broadcast=form.message_broadcast.data,
                                            token_generate=form.token_generate.data,
                                            token_invalidate=form.token_invalidate.data,
                                            ))
              for _ in range(0, form.count.data or 1)]
    db.session.add_all(tokens)
    db.session.commit()
    return "<br >".join([str(tk.id) for tk in tokens])
