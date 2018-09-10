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
    task = request.args.get("task", None) if request.method == 'GET' else None
    count = request.args.get("count", None) if request.method == 'GET' else None

    if room and task:
        output = ""
        if not source:
            source = ''
        for i in range(0, count or 1):
            if i > 0:
                output += ";"
            output += Token.create(source, room, task).uuid()
        return output

    form = TokenGenerationForm()
    form.room.choices = [(room.id(), room.name()) for room in Room.list()]
    form.task.choices = [(task.id(), task.name()) for task in Task.list()]
    if form.is_submitted():
        output = ""
        for i in range(0, form.count.data):
            source = form.source.data
            room = Room.from_id(form.room.data)
            task = Task.from_id(form.task.data)
            output += Token.create(source, room, task).uuid()
            output += "<br />"
        return output
    return render_template('token.html', form=form, title=config['templates']['token-title'])


@main.route('/', methods=['GET', 'POST'])
def index():
    login_token = request.args.get("token", None) if request.method == 'GET' else None
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
            form.token.errors.append("The token is either expired, was already used or isn't correct at all.")
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

    default_layout = config['templates'].get('default-layout')
    if default_layout:
        layout = Layout.from_json_file(default_layout)
        html = layout.html()
        css = layout.css()
    else:
        html = ""
        css = ""
    return render_template('chat.html',
                           name=name,
                           room=room.label(),
                           title=config['templates']['chat-title'],
                           heading=config['templates']['chat-header'],
                           refresh_threshold=config['client']['refresh-threshold'],
                           refresh_start=config['client']['refresh-start'],
                           refresh_max=config['client']['refresh-max'],
                           ping_pong_latency_checks=config['client']['ping-pong-latency-checks'],
                           html=html,
                           css=css,
                           )


@main.route('/test', methods=['GET', 'POST'])
def test():
    name = request.args.get("layout", None) if request.method == 'GET' else None
    layout = Layout.from_json_file(name)
    if not name:
        return ""
    return render_template('layout.html',
                           title=name,
                           html=layout.html(),
                           css=layout.css()
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
