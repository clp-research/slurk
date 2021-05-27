from app.openvidu import Session
from flask import g, make_response, jsonify, Blueprint, request, current_app
from flask_httpauth import HTTPTokenAuth
from werkzeug.exceptions import BadRequest, Unauthorized, Forbidden, NotFound
from logging import getLogger

from sqlalchemy.exc import StatementError, IntegrityError

from .. import socketio
from ..models import Token, Layout, Task, Permissions, Room, User
from .log import log_event

auth = HTTPTokenAuth(scheme='Token')
api = Blueprint('api', __name__, url_prefix="/api/v2/")


def abort(ex):
    from flask import abort
    abort(make_response({'error': ex.description}, ex.code))


@api.errorhandler(Exception)
def handle_exception(ex):
    abort(BadRequest(str(ex)))


@auth.error_handler
def unauthorized():
    abort(Unauthorized)


def get_json(request):
    if request.data != b'' and not request.is_json:
        abort(BadRequest(description="Data has to be passed as JSON string"))
    return request.json or {}


@auth.verify_token
def verify_token(token):
    db = current_app.session
    try:
        token = db.query(Token).get(token)
    except StatementError:
        return False
    if token:
        g.current_permissions = token.permissions
        g.current_user = token.user
        return True
    return False


@api.route('/layouts', methods=['GET'])
@auth.login_required
def get_layouts():
    if not g.current_permissions.layout_query:
        return make_response(jsonify({'error': 'insufficient rights'}), 403)

    return jsonify([dict(uri=f'/layout/{layout.id}', **layout.as_dict())
                    for layout in current_app.session.query(Layout).all()])


@api.route('/layout/<int:id>', methods=['GET'])
@auth.login_required
def get_layout(id):
    if not g.current_permissions.layout_query:
        return make_response(jsonify({'error': 'insufficient rights'}), 403)

    db = current_app.session
    layout = db.query(Layout).get(id)
    if layout:
        return jsonify(layout.as_dict())
    else:
        return make_response(jsonify({'error': 'layout not found'}), 404)


@api.route('/layout', methods=['POST'])
@auth.login_required
def post_layout():
    if not g.current_permissions.layout_create:
        return make_response(jsonify({'error': 'insufficient rights'}), 403)

    data = request.get_json(force=True) if request.is_json else None
    if not data:
        return make_response(jsonify({'error': 'bad request'}, 400))

    try:
        name = data.get("title")
        if not name:
            name = data.get("subtitle", "Unnamed")
        layout = Layout.from_json_data(name, data)
        db = current_app.session
        db.add(layout)
        db.commit()
        return jsonify(layout.as_dict())
    except (IntegrityError, StatementError) as e:
        return make_response(jsonify({'error': str(e)}), 400)


@api.route('/layout/<int:id>', methods=['PUT'])
@auth.login_required
def put_layout(id):
    if not g.current_permissions.layout_update:
        return make_response(jsonify({'error': 'insufficient rights'}), 403)

    data = get_json(request)

    db = current_app.session
    layout = db.query(Layout).get(id)
    if not layout:
        return make_response(jsonify({'error': 'layout not found'}), 404)

    new_layout = Layout.from_json_data("", data)
    if 'css' in data:
        layout.css = new_layout.css
    if 'html' in data:
        layout.html = new_layout.html
    if 'name' in data:
        layout.name = data['name']
    if 'scripts' in data:
        layout.script = new_layout.script
    if 'subtitle' in data:
        layout.subtitle = new_layout.subtitle
    if 'title' in data:
        layout.title = new_layout.title

    try:
        db.commit()
        return jsonify(layout.as_dict())
    except (IntegrityError, StatementError) as e:
        return make_response(jsonify({'error': str(e)}), 400)


@api.route('/tokens', methods=['GET'])
@auth.login_required
def get_tokens():
    if not g.current_permissions.token_query:
        abort(Forbidden)

    db = current_app.session
    return jsonify({str(token.id): token.as_dict() for token in db.query(Token).all()})


@api.route('/token/<string:id>', methods=['GET'])
@auth.login_required
def get_token(id):
    if not g.current_permissions.token_query and not (g.current_user and str(g.current_user.token) == id):
        abort(Forbidden)

    db = current_app.session

    token = db.query(Token).get(id)
    if token:
        return make_response(token.as_dict())
    else:
        return make_response(jsonify({'error': 'token not found'}), 404)


@api.route('/token', methods=['POST'])
@auth.login_required
def post_token():
    if not g.current_permissions.token_generate:
        abort(Forbidden)

    data = get_json(request)

    db = current_app.session
    if 'task' in data and data['task']:
        task = db.query(Task).get(data['task'])
        if not task:
            abort(NotFound(description='task not found'))
    else:
        task = None

    if 'room' in data and data['room']:
        room = db.query(Room).get(data['room'])
        if not room:
            abort(NotFound(description='room not found'))
    else:
        room = None

    token = Token(
        task=task,
        room=room,
        source=data.get("source", None),
        permissions=Permissions(
            user_query=data.get("user_query", False),
            user_log_event=data.get("user_log_event", False),
            user_room_join=data.get("user_room_join", False),
            user_room_leave=data.get("user_room_leave", False),
            message_text=data.get("message_text", False),
            message_image=data.get("message_image", False),
            message_command=data.get("message_command", False),
            message_broadcast=data.get("message_broadcast", False),
            audio_join=data.get("audio_join", False),
            audio_publish=data.get("audio_publish", False),
            video_join=data.get("video_join", False),
            video_publish=data.get("video_publish", False),
            room_query=data.get("room_query", False),
            room_log_query=data.get("room_log_query", False),
            room_create=data.get("room_create", False),
            room_update=data.get("room_update", False),
            room_delete=data.get("room_delete", False),
            layout_query=data.get("layout_query", False),
            layout_create=data.get("layout_create", False),
            layout_update=data.get("layout_update", False),
            task_create=data.get("task_create", False),
            task_query=data.get("task_query", False),
            task_update=data.get("task_update", False),
            token_generate=data.get("token_generate", False),
            token_query=data.get("token_query", False),
            token_update=data.get("token_update", False),
            token_invalidate=data.get("token_invalidate", False),
        )
    )
    db.add(token)
    db.commit()

    return make_response(token.as_dict())


@api.route('/token/<string:id>', methods=['DELETE'])
@auth.login_required
def invalidate_token(id):
    if not g.current_permissions.token_invalidate:
        abort(Forbidden)

    db = current_app.session
    token = db.query(Token).get(id)
    if not token:
        abort(NotFound(description='token not found'))

    token.valid = False
    db.commit()
    return jsonify(token.as_dict())


@api.route('/users', methods=['GET'])
@auth.login_required
def get_users():
    db = current_app.session
    return jsonify([dict(uri=f'/users/{user.id}', **user.as_dict()) for user in db.query(User).all()])


@api.route('/user/<int:id>', methods=['GET'])
@auth.login_required
def get_user(id):
    if id != g.current_user.id and not g.current_permissions.user_query:
        getLogger('slurk').warning(f'get_user: insufficient rights for user {g.current_user.id}')
        return make_response(jsonify({'error': 'insufficient rights'}), 403)
    db = current_app.session
    user = db.query(User).get(id) if id != g.current_user.id else g.current_user
    if user:
        return jsonify(user.as_dict())
    else:
        return make_response(jsonify({'error': 'user not found'}), 404)


@api.route('/tasks', methods=['GET'])
@auth.login_required
def get_tasks():
    if not g.current_permissions.task_query:
        return make_response(jsonify({'error': 'insufficient rights'}), 403)

    db = current_app.session
    return jsonify([dict(uri=f'/task/{task.id}', **task.as_dict()) for task in db.query(Task).all()])


@api.route('/task/<int:id>', methods=['GET'])
@auth.login_required
def get_task(id):
    if not g.current_permissions.task_query:
        return make_response(jsonify({'error': 'insufficient rights'}), 403)

    db = current_app.session
    task = db.query(Task).get(id)
    if task:
        return jsonify(task.as_dict())
    else:
        return make_response(jsonify({'error': 'task not found'}), 404)


@api.route('/task', methods=['POST'])
@auth.login_required
def post_task():
    if not g.current_permissions.task_create:
        return make_response(jsonify({'error': 'insufficient rights'}), 403)

    data = request.get_json(force=True) if request.is_json else None
    if not data:
        return make_response(jsonify({'error': 'bad request'}, 400))

    name = data.get('name')
    num_users = data.get('num_users')
    if not name:
        return make_response(jsonify({'error': 'missing parameter: `name`'}, 400))
    if not num_users:
        return make_response(jsonify({'error': 'missing parameter: `num_users`'}, 400))
    try:
        num_users = int(num_users)
    except ValueError:
        return make_response(jsonify({'error': 'invalid number: `num_users`'}, 400))

    db = current_app.session
    if 'layout' in data and data['layout']:
        layout = db.query(Layout).get(data['layout'])
        if not layout:
            return make_response(jsonify({'error': 'layout not found'}), 404)
    else:
        layout = db.query(Layout).filter(Layout.name == "default").first()

    try:
        task = Task(
            name=name,
            num_users=num_users,
            layout=layout,
        )
        db.add(task)
        db.commit()
        return jsonify(task.as_dict())
    except (IntegrityError, StatementError) as e:
        return make_response(jsonify({'error': str(e)}), 400)


@api.route('/task/<int:id>', methods=['PUT'])
@auth.login_required
def put_task(id):
    if not g.current_permissions.task_update:
        return make_response(jsonify({'error': 'insufficient rights'}), 403)

    data = request.get_json(force=True) if request.is_json else None
    if not data:
        return make_response(jsonify({'error': 'bad request'}, 400))

    db = current_app.session
    task = db.query(Task).get(id)
    if not task:
        return make_response(jsonify({'error': 'room not found'}), 404)

    try:
        if 'num_users' in data:
            try:
                task.num_users = int(data['num_users'])
            except ValueError:
                return make_response(jsonify({'error': 'invalid number: `num_users`'}, 400))
        if 'name' in data:
            task.name = data['name']
        if 'layout' in data and data['layout']:
            layout = db.query(Layout).get(data['layout'])
            if not layout:
                return make_response(jsonify({'error': 'layout not found'}), 404)
            task.layout = layout

        db.commit()
        return jsonify(task.as_dict())
    except (IntegrityError, StatementError, ValueError) as e:
        return make_response(jsonify({'error': str(e)}), 400)


@api.route('/rooms', methods=['GET'])
@auth.login_required
def get_rooms():
    if not g.current_permissions.room_query:
        return make_response(jsonify({'error': 'insufficient rights'}), 403)

    return jsonify([dict(uri='/rooms', **room.as_dict()) for room in current_app.session.query(Room).all()])


@api.route('/room/<string:name>', methods=['GET'])
@auth.login_required
def get_room(name):
    if name not in g.current_user.room_names and not g.current_permissions.room_query:
        getLogger('slurk').warning(f'get_room: insufficient rights for user {g.current_user.id}')
        getLogger('slurk').warning(f'room: {name}')
        getLogger('slurk').warning(f'current_user: {g.current_user.as_dict()}')

        return make_response(jsonify({'error': 'insufficient rights'}), 403)

    room = current_app.session.query(Room).get(name)
    if room:
        return jsonify(dict(uri=f'/room/{room.name}', **room.as_dict()))
    else:
        return make_response(jsonify({'error': 'room not found'}), 404)


@api.route('/room/<string:name>/layout', methods=['GET'])
@auth.login_required
def get_room_layout(name):
    db = current_app.session
    if name not in g.current_user.room_names and (
            not g.current_permissions.room_query or not g.current_permissions.layout_query):
        getLogger('slurk').warning(f'get_room_layout: insufficient rights for user {g.current_user.id}')
        return make_response(jsonify({'error': 'insufficient rights'}), 403)

    room = db.query(Room).get(name)
    if room:
        return jsonify(room.layout.as_dict())
    else:
        return make_response(jsonify({'error': 'room not found'}), 404)


@api.route('/room', methods=['POST'])
@auth.login_required
def post_room():
    if not g.current_permissions.room_create:
        return make_response(jsonify({'error': 'insufficient rights'}), 403)

    data = request.get_json(force=True) if request.is_json else None
    if not data:
        return make_response(jsonify({'error': 'bad request'}, 400))

    name = data.get('name')
    label = data.get('label')
    if not name:
        return make_response(jsonify({'error': 'missing parameter: `name`'}, 400))
    if not label:
        return make_response(jsonify({'error': 'missing parameter: `label`'}, 400))

    db = current_app.session
    if 'layout' in data and data['layout']:
        layout = db.query(Layout).get(data['layout'])
        if not layout:
            return make_response(jsonify({'error': 'layout not found'}), 404)
    else:
        layout = db.query(Layout).filter(Layout.name == "default").first()

    try:
        room = Room(
            name=name,
            label=label,
            layout=layout,
            read_only=data.get('read_only'),
            show_users=data.get('show_users'),
            show_latency=data.get('show_latency'),
            static=data.get('static'),
            openvidu_session=current_app.openvidu.initialize_session().id if current_app.openvidu else None
        )
        db.add(room)
        db.commit()
        return jsonify(room.as_dict())
    except (IntegrityError, StatementError) as e:
        return make_response(jsonify({'error': str(e)}), 400)


@api.route('/room/<string:name>', methods=['PUT'])
@auth.login_required
def put_rooms(name):
    if not g.current_permissions.room_update:
        return make_response(jsonify({'error': 'insufficient rights'}), 403)

    data = request.get_json(force=True) if request.is_json else None
    if not data:
        return make_response(jsonify({'error': 'bad request'}, 400))

    db = current_app.session
    room = db.query(Room).get(name)
    if not room:
        return make_response(jsonify({'error': 'room not found'}), 404)

    try:
        if 'label' in data:
            room.label = data['label']
        if 'layout' in data and data['layout']:
            layout = db.query(Layout).get(data['layout'])
            if not layout:
                return make_response(jsonify({'error': 'layout not found'}), 404)
            room.layout = layout
        if 'read_only' in data:
            room.read_only = data['read_only']
        if 'show_users' in data:
            room.show_users = data['show_users']
        if 'show_latency' in data:
            room.show_users = data['show_latency']
        if 'static' in data:
            room.static = data['static']

        db.commit()
        return jsonify(room.as_dict())
    except (IntegrityError, StatementError) as e:
        return make_response(jsonify({'error': str(e)}), 400)


@api.route('/room/<string:name>', methods=['DELETE'])
@auth.login_required
def delete_rooms(name):
    if not g.current_permissions.room_delete:
        return make_response(jsonify({'error': 'insufficient rights'}), 403)

    db = current_app.session
    room = db.query(Room).get(name)
    if not room:
        return make_response(jsonify({'error': 'room not found'}), 404)

    if current_app.openvidu:
        Session(current_app.openvidu, room.openvidu_session).close()
    try:
        for user in room.current_users:
            if user.session_id:
                socketio.emit('left_room', room.name, room=user.session_id)
                log_event("leave", user, room)
        socketio.close_room(room.name)
        db.query(Room).filter_by(name=room.name).delete()
        db.commit()
        return jsonify({'result': True})
    except IntegrityError as e:
        return make_response(jsonify({'error': str(e)}), 400)


@api.route('/room/<string:name>/logs', methods=['GET'])
@auth.login_required
def get_room_logs(name):
    if not g.current_permissions.room_log_query:
        getLogger('slurk').warning(f'get_room_logs: insufficient rights for user {g.current_user.id}')
        return make_response(jsonify({'error': 'insufficient rights'}), 403)

    db = current_app.session
    room = db.query(Room).get(name)
    if room:
        return jsonify([log.as_dict() for log in room.logs])
    else:
        return make_response(jsonify({'error': 'room not found'}), 404)


@api.route('/user/<int:id>/logs', methods=['GET'])
@auth.login_required
def get_user_logs(id):
    def filter_private_messages(logs, id):
        for log in logs:
            if log['event'] == "text_message" or log['event'] == "image_message":
                # Filter only messages
                if log['receiver']:
                    # Private message
                    if int(log['receiver']) != id and log['user']['id'] != id:
                        # User not affected, continue the loop
                        continue
            yield log

    db = current_app.session
    user = db.query(User).get(id)
    if user:
        return jsonify({room.name: list(filter_private_messages([log.as_dict() for log in room.logs], user.id))
                        for room in user.rooms})
    else:
        return make_response(jsonify({'error': 'user not found'}), 404)


@api.route('/user/<int:id>/task', methods=['GET'])
@auth.login_required
def get_user_task(id):
    db = current_app.session
    user = db.query(User).get(id)
    if user:
        return jsonify(user.token.task.as_dict() if user.token.task else None)
    else:
        return make_response(jsonify({'error': 'user not found'}), 404)


@api.route('/user/<int:id>/log', methods=['POST'])
@auth.login_required
def post_user_logs(id):
    if not g.current_permissions.user_log_event:
        return make_response(jsonify({'error': 'insufficient rights'}), 403)

    db = current_app.session
    user = db.query(User).get(id)
    if not user:
        return make_response(jsonify({'error': 'user not found'}), 404)

    data = request.get_json(force=True) if request.is_json else None
    if not data:
        return make_response(jsonify({'error': 'bad request'}, 400))

    event = data.get('event')
    if not event:
        return make_response(jsonify({'error': 'missing parameter: `event`'}, 400))

    if 'room' in data:
        room = db.query(Room).get(data['room'])
        if not room:
            return make_response(jsonify({'error': 'room not found'}), 404)
    else:
        room = None

    try:
        return jsonify(log_event(event, user, room, data.get('data')).as_dict())
    except (IntegrityError, StatementError) as e:
        return make_response(jsonify({'error': str(e)}), 400)
