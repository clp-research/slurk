from calendar import timegm
from copy import deepcopy
from datetime import datetime

from flask import request
from flask_login import login_required, current_user, logout_user
from flask_socketio import emit

from .Task import Task
from .Token import Token
from .Room import Room, ROOMS
from .User import User
from .Permissions import Permissions
from .Layout import Layout
from .. import socketio

from .. import config


def request_new_image(_name, room, data):
    if len(data) < 1:
        return

    if len(data) > 1:
        receiver = User.from_id(data[1])
        if not receiver:
            return

        emit('new_image', {
            'url': data[0],
            'user': current_user.serialize(),
            'timestamp': timegm(datetime.now().utctimetuple())
        }, room=receiver.sid())
        log({'type': "new_image", 'room': room.id(), 'url': data[0], 'receiver': receiver.id()})
    else:
        emit('new_image', {
            'url': data[0],
            'user': current_user.serialize(),
            'timestamp': timegm(datetime.now().utctimetuple())
        }, room=room.name())
        log({'type': "new_image", 'room': room.id(), 'url': data[0]})

@socketio.on('mousePosition', namespace='/chat')
def mouse_position(data):
    emit('mouse_position', {
        'type': data['type'],
        'coordinates': data['coordinates'],
        'element': data['element'],
        'user': current_user.serialize(),
        'timestamp': timegm(datetime.now().utctimetuple()),
    }, room=Room.from_id(data['room']).name())

@socketio.on('transferFilePath', namespace='/chat')
def file_transfer(data):
    emit('file_path', {'type': data['type'], 'file': data['file']}, room=Room.from_id(data['room']).name())

@socketio.on('connectWithToken', namespace='/login')
def connect_with_token(data):
    logout_user()

    token = Token.from_uuid(data['token'])
    name = data['name']

    user = User.login(name, token)
    if not user:
        emit("login_status", {'success': False, 'message': 'Invalid token or username'})
    else:
        emit("login_status", {'success': True, 'message': ''})


@socketio.on('connect', namespace='/chat')
@login_required
def connect():
    current_user.set_sid(request.sid)
    print(current_user.name(), "connected")
    latest_room = current_user.latest_room()
    if latest_room:
        current_user.join_room(latest_room)
    else:
        current_user.join_room(current_user.token().room())


@socketio.on('my_ping', namespace='/chat')
@login_required
def ping():
    emit('my_pong', {
        'timestamp': timegm(datetime.now().utctimetuple())
    }, room=request.sid)


@socketio.on('join_room', namespace='/chat')
@login_required
def join_room(data):
    User.from_id(data['user']).join_room(Room.from_id(data['room']))


@socketio.on('leave_room', namespace='/chat')
@login_required
def leave_room(data):
    User.from_id(data['user'] if 'user' in data else current_user.id()).leave_room(Room.from_id(data['room']))


@socketio.on('disconnect', namespace='/chat')
@login_required
def disconnect():
    for room in current_user.rooms():
        current_user.leave_room(room)
    print(current_user.name(), "disconnected")
    logout_user()


@socketio.on('log', namespace='/chat')
@login_required
def log(data):
    if 'room' not in data:
        print("logging requires a room")
        return

    room = data['room']
    if isinstance(room, int) or isinstance(room, str):
        data['room'] = Room.from_id(room).serialize()
    elif not isinstance(room, Room):
        raise TypeError(f"Object of type `int`, `str` or `Room` expected, however type `{type(room)}` was passed")

    if room not in ROOMS:
        print("Could not log")
        return

    if 'user' not in data:
        data['user'] = current_user.serialize()
    else:
        user = data['user']
        if isinstance(user, int) or not isinstance(user, str):
            data['user'] = User.from_id(user).serialize()

    if 'type' not in data:
        data['type'] = "custom"

    ROOMS[room]['log'].append(data)


@socketio.on('open_task_room', namespace='/chat')
@login_required
def open_task_room(data):
    show_users_string = config["client"]["show-users"].lower()
    show_latency_string = config["client"]["show-latency"].lower()
    read_only = False
    show_users = show_users_string == "on" or show_users_string == "yes" or show_users_string == "true"
    show_latency = show_latency_string == "on" or show_latency_string == "yes" or show_latency_string == "true"
    show_input = True
    show_history = True
    show_interaction_area = True

    if 'hide' in data:
        if 'users' in data['hide']:
            show_users = False
        if 'latency' in data['hide']:
            show_latency = False
        if 'input' in data['hide']:
            show_input = False
        if 'history' in data['hide']:
            show_history = False
        if 'interaction_area' in data['hide']:
            show_interaction_area = False

    layout = data.get('layout')
    if not layout:
        if Layout.from_json_file(data['label']):
            layout = data['label']
        else:
            layout = ""

    room = Room.create(data['name'], data['label'],
                       layout=layout,
                       read_only=read_only,
                       show_users=show_users,
                       show_latency=show_latency,
                       show_input=show_input,
                       show_history=show_history,
                       show_interaction_area=show_interaction_area)
    users = [User.from_id(user) for user in data['users']]
    for user in users:
        user.leave_room(user.latest_room())
        user.join_room(room)
    emit('new_task_room', {
        'users': [user.serialize() for user in users],
        'task': Task.from_id(data['task']).serialize(),
        'room': room.serialize()
    }, room=current_user.latest_room().name())


@socketio.on('invalidate_token', namespace='/chat')
@login_required
def invalidate_token(data):
    Token.from_id(data['token']).invalidate()


@socketio.on('text', namespace='/chat')
@login_required
def text(data):
    if 'receiver_id' in data:
        user = User.from_id(data['receiver_id'])
        print(f"private message: {data['msg']}")
        emit('message', {
            'msg': data['msg'],
            'user': current_user.serialize(),
            'timestamp': timegm(datetime.now().utctimetuple()),
        }, room=user.sid())
        log({'type': 'text', 'msg': data['msg'], 'room': user.latest_room().id(), 'receiver': data['receiver_id']})
    elif 'room' in data:
        print(f"room message: {data['msg']}")
        emit('message', {
            'msg': data['msg'],
            'user': current_user.serialize(),
            'timestamp': timegm(datetime.now().utctimetuple()),
        }, room=Room.from_id(data['room']).name())
        log({'type': 'text', 'msg': data['msg'], 'room': data['room']})
    else:
        print("`text` requires `room` and optionally `receiver_id` as parameters")
        return


@socketio.on('image', namespace='/chat')
@login_required
def image(data):
    if 'receiver_id' in data:
        user = User.from_id(data['receiver_id'])
        print(f"private image: {data['image']}")
        emit('message', {
            'image': data['image'],
            'user': current_user.serialize(),
            'width': data['width'] if 'width' in data else None,
            'height': data['width'] if 'width' in data else None,
            'timestamp': timegm(datetime.now().utctimetuple()),
        }, room=user.sid())
        log({'type': 'image', 'msg': data['image'], 'room': user.latest_room().id(), 'receiver': data['receiver_id']})
    elif 'room' in data:
        print(f"room image: {data['image']}")
        emit('message', {
            'image': data['image'],
            'user': current_user.serialize(),
            'width': data['width'] if 'width' in data else None,
            'height': data['height'] if 'height' in data else None,
            'timestamp': timegm(datetime.now().utctimetuple()),
        }, room=Room.from_id(data['room']).name())
        log({'type': 'image', 'msg': data['image'], 'room': data['room']})
    else:
        print("`image` requires `room` and optionally `receiver_id` as parameters")
        return


@socketio.on('update_info', namespace='/chat')
@login_required
def update_info(data):
    target = None
    if 'receiver_id' in data:
        target_id = data['receiver_id']
        if not isinstance(target_id, int) and not isinstance(target_id, str):
            raise TypeError(f"Object of type `int` or `str` expected, however type `{type(target_id)}` was passed")
        target = User.from_id(target_id).sid()
    elif 'room' in data:
        target_id = data['room']
        if not isinstance(target_id, int) and not isinstance(target_id, str):
            raise TypeError(f"Object of type `int` or `str` expected, however type `{type(target_id)}` was passed")
        target = Room.from_id(target_id).name()
    else:
        print("Updating info requires either a receiver id or a target")

    if 'text' in data:
        emit('update_info_text', {'text': data["text"]}, room=target)


@socketio.on('join_task', namespace='/chat')
@login_required
def join_task(data):
    if 'room' not in data:
        print("joining task requires a room")
        return

    room = data['room']
    if not isinstance(room, int) and not isinstance(room, str):
        raise TypeError(f"Object of type `int` or `str` expected, however type `{type(room)}` was passed")

    current_user.join_room(Room.from_id(room))


def listen_to(_user, room, data):
    room_id = room.id()
    if data[0] not in ROOMS[room_id]['listeners']:
        ROOMS[room_id]['listeners'][data[0]] = {deepcopy(current_user)}
    else:
        ROOMS[room_id]['listeners'][data[0]].add(deepcopy(current_user))


@socketio.on('get_permissions', namespace='/chat')
@login_required
def get_permissions(data):
    if 'user' not in data:
        print("asking for permission requires a user")
        return
    if 'room' not in data:
        print("asking for permission requires a room")
        return

    if not isinstance(data['room'], int) and not isinstance(data['room'], str):
        raise TypeError(f"Object of type `int` or `str` expected, however type `{type(data['room'])}` was passed")
    if not isinstance(data['user'], int) and not isinstance(data['user'], str):
        raise TypeError(f"Object of type `int` or `str` expected, however type `{type(data['user'])}` was passed")
    room = Room.from_id(data['room'])
    user = User.from_id(data['user'])

    emit('permissions', {
        'user': user.serialize(),
        'room': room.serialize(),
        'permissions': Permissions(user.token(), room).serialize()
    }, room=request.sid)


@socketio.on('update_permissions', namespace='/chat')
@login_required
def update_permissions(data):
    if 'user' not in data:
        print("updating permission requires a user")
        return
    if 'room' not in data:
        print("updating permission requires a room")
        return

    if not isinstance(data['room'], int) and not isinstance(data['room'], str):
        raise TypeError(f"Object of type `int` or `str` expected, however type `{type(data['room'])}` was passed")
    if not isinstance(data['user'], int) and not isinstance(data['user'], str):
        raise TypeError(f"Object of type `int` or `str` expected, however type `{type(data['user'])}` was passed")
    room = Room.from_id(data['room'])
    user = User.from_id(data['user'])

    print(data)

    permissions = Permissions(user.token(), room)

    if 'write' in data:
        permissions.set_write(data['write'])
    if 'users' in data:
        permissions.set_see_users(data['users'])
    if 'latency' in data:
        permissions.set_see_latency(data['latency'])
    if 'input' in data:
        permissions.set_see_input(data['input'])
    if 'history' in data:
        permissions.set_see_history(data['history'])
    if 'interaction_area' in data:
        permissions.set_see_interaction_area(data['interaction_area'])

    emit('update_permissions', {
        'permissions': permissions.serialize()
    }, room=user.sid())


@socketio.on('command', namespace='/chat')
@login_required
def command(message):
    global listeners

    if 'room' not in message:
        return
    room = Room.from_id(message['room'])

    def get_command_function(command_string):
        return {
            'new_image': request_new_image,
            'listen_to': listen_to
        }.get(command_string, None)

    cmd = get_command_function(message['data'][0])
    if cmd:
        cmd(current_user, room, message['data'][1:])
    else:
        clients = ROOMS[room.id()]['listeners'].get(message['data'][0], None)
        if clients:
            for listener in clients:
                emit(message['data'][0], {
                    'user': current_user.serialize(),
                    'timestamp': timegm(datetime.now().utctimetuple()),
                    'data': message['data'][1:],
                    'room': room.serialize()
                }, room=listener.sid())
        else:
            emit('status', {
                'type': 'undefined_command',
                'command': message['data'][0],
                'timestamp': timegm(datetime.now().utctimetuple())
            }, room=request.sid)

    log({'type': 'command', 'room': room.id(), 'command': message['data'][0], 'data': message['data'][1:]})


@socketio.on('keypress', namespace='/chat')
@login_required
def keypress():
    emit('start_typing', {'user': current_user.serialize()}, room=current_user.room())


@socketio.on('clear_chat', namespace='/chat')
@login_required
def clear_chat(data):
    if 'receiver_id' in data:
        user = User.from_id(data['receiver_id'])
        emit('clear_chat_area', {
            'timestamp': timegm(datetime.now().utctimetuple()),
        }, room=user.sid())
    elif 'room' in data:
        emit('clear_chat_area', {
            'timestamp': timegm(datetime.now().utctimetuple()),
        }, room=Room.from_id(data['room']).name())
    else:
        print("`clear_chat` requires `room` and optionally `receiver_id` as parameters")
        return
