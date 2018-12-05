import os

from flask import redirect, url_for, render_template, request, jsonify, abort

from .Room import Room
from .Permissions import Permissions
from .Task import Task
from .Token import Token
from .Layout import Layout
from . import main
from .forms import LoginForm, TokenGenerationForm
from .User import User
from flask_login import login_required, current_user, logout_user

from .. import config


@main.route('/token', methods=['GET', 'POST'])
def token():
    source = request.args.get("source", None) if request.method == 'GET' else None
    room = request.args.get("room", None) if request.method == 'GET' else None
    if room:
        room = int(room)
    task = request.args.get("task", None) if request.method == 'GET' else None
    if task:
        task = int(task)
    count = request.args.get("count", None) if request.method == 'GET' else None
    if count:
        count = int(count)
    key = request.args.get("key", None) if request.method == 'GET' else None

    form = TokenGenerationForm(task=task or 0, count=count or 1, source=source or "", key=key or "", room=room or 1)
    if form.is_submitted():
        source = form.source.data or ""
        room = form.room.data
        task = form.task.data
        count = form.count.data
        key = form.key.data
    elif not (room and task and key):
        form.room.choices = [(room.id(), room.name()) for room in Room.list()]
        form.task.choices = [(task.id(), task.name()) for task in Task.list()]
        return render_template('token.html',
                               form=form,
                               title=config['templates']['token-title'],
                               )

    if key != config["server"]["secret-key"]:
        return "Invalid password"
    output = ""
    for i in range(0, count or 1):
        output += Token.create(source or "", Room.from_id(room), Task.from_id(task)).uuid()
        output += "<br />"
    return output



@main.route('/', methods=['GET', 'POST'])
def index():
    login_token = request.args.get(
        "token", None) if request.method == 'GET' else None
    name = request.args.get("name", None) if request.method == 'GET' else None

    token_invalid = False
    if name and login_token:
        login = User.login(name, Token.from_uuid(login_token))
        if login:
            return redirect(url_for('.chat'))
        token_invalid = True

    form = LoginForm()
    if form.validate_on_submit():
        name = form.name.data
        login_token = form.token.data
        user = User.login(form.name.data, Token.from_uuid(form.token.data))
        if user:
            return redirect(url_for('.chat'))
        else:
            form.token.errors.append(
                "The token is either expired, was already used or isn't correct at all.")
    if name:
        form.name.data = name
    return render_template('index.html', form=form, token=login_token, token_invalid=token_invalid,
                           title=config['templates']['login-title'])


@main.route('/chat')
@login_required
def chat():
    room = current_user.latest_room()
    token = current_user.token()
    if not room:
        room = token.room()
    name = current_user.name()

    permissions = Permissions(token, room)
    print(permissions)

    if name == '' or room == '':
        return redirect(url_for('.index'))

    return render_template('chat.html',
                           name=name,
                           room=room.label(),
                           title=config['templates']['chat-title'],
                           heading=config['templates']['chat-header'],
                           refresh_threshold=config['client']['refresh-threshold'],
                           refresh_start=config['client']['refresh-start'],
                           refresh_max=config['client']['refresh-max'],
                           ping_pong_latency_checks=config['client']['ping-pong-latency-checks'],
                           )


@main.route('/test', methods=['GET', 'POST'])
def test():
    name = request.args.get(
        "layout", None) if request.method == 'GET' else None
    layout = Layout.from_json_file(name)
    if not name:
        return ""
    return render_template('layout.html',
                           title=name,
                           html=layout.html(indent=8),
                           css=layout.css(indent=12),
                           script=layout.script(),
                           )


# @login_required
@main.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    message = request.form.get('message', None)
    if message:
        return message
    else:
        return "Logout successful"
