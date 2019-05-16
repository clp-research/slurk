from flask import g
from flask_httpauth import HTTPTokenAuth

from sqlalchemy.exc import StatementError, IntegrityError

from ..models.log import Log

from .room import *
from .token import *
from .user import *
from .task import *


from flask import Blueprint, request

auth = HTTPTokenAuth(scheme='Token')
api = Blueprint('api', __name__, url_prefix="/api/v2/")


@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 401)


@auth.verify_token
def verify_token(token):
    try:
        token = Token.query.get(token)
    except StatementError:
        return False
    if token:
        g.current_permissions = token.permissions
        g.current_user = token.user
        return True
    return False


@api.route('/users', methods=['GET'])
@auth.login_required
def get_users():
    return jsonify([dict(uri="/users/"+str(user.id), **user.as_dict()) for user in User.query.all()])


@api.route('/users/<int:id>', methods=['GET'])
@auth.login_required
def get_user(id):
    user = User.query.get(id)
    if user:
        return jsonify(user.as_dict())
    else:
        return make_response(jsonify({'error': 'user not found'}), 404)


@api.route('/rooms', methods=['GET'])
@auth.login_required
def get_rooms():
    return jsonify([dict(uri="/rooms/"+room.name, **room.as_dict()) for room in Room.query.all()])


@api.route('/rooms/<string:name>', methods=['GET'])
@auth.login_required
def get_room(name):
    room = Room.query.get(name)
    if room:
        return jsonify(room.as_dict())
    else:
        return make_response(jsonify({'error': 'room not found'}), 404)


@api.route('/rooms', methods=['POST'])
@auth.login_required
def post_rooms():
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

    if 'layout' in data and data['layout']:
        layout = Layout.query.get(data['layout'])
        if not layout:
            return make_response(jsonify({'error': 'layout not found'}), 404)
    else:
        layout = None

    try:
        room = Room(
            name=name,
            label=label,
            layout=layout,
            read_only=data.get('read_only'),
            show_users=data.get('show_users'),
            show_latency=data.get('show_latency'),
            static=data.get('static'),
        )
        db.session.add(room)
        db.session.commit()
        return jsonify(room.as_dict())
    except (IntegrityError, StatementError) as e:
        return make_response(jsonify({'error': str(e)}), 400)


@api.route('/rooms/<string:name>', methods=['PUT'])
@auth.login_required
def put_rooms(name):
    if not g.current_permissions.room_update:
        return make_response(jsonify({'error': 'insufficient rights'}), 403)

    data = request.get_json(force=True) if request.is_json else None
    if not data:
        return make_response(jsonify({'error': 'bad request'}, 400))

    room = Room.query.get(name)
    if not room:
        return make_response(jsonify({'error': 'room not found'}), 404)

    try:
        if 'label' in data:
            room.label = data['label']
        if 'layout' in data and data['layout']:
            layout = Layout.query.get(data['layout'])
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

        db.session.commit()
        return jsonify(room.as_dict())
    except (IntegrityError, StatementError) as e:
        return make_response(jsonify({'error': str(e)}), 400)


@api.route('/rooms/<string:name>', methods=['DELETE'])
@auth.login_required
def delete_rooms(name):
    if not g.current_permissions.room_delete:
        return make_response(jsonify({'error': 'insufficient rights'}), 403)

    room = Room.query.get(name)
    if not room:
        return make_response(jsonify({'error': 'room not found'}), 404)

    try:
        for user in room.current_users:
            if user.session_id:
                socketio.emit('left_room', room.name, room=user.session_id)
                log_event("leave", user, room)
        socketio.close_room(room.name)
        Room.query.filter_by(name=room.name).delete()
        db.session.commit()
        return jsonify({'result': True})
    except IntegrityError as e:
        return make_response(jsonify({'error': str(e)}), 400)


@api.route('/layouts', methods=['GET'])
@auth.login_required
def get_layouts():
    return jsonify([dict(uri="/layouts/"+str(layout.id), **layout.as_dict()) for layout in Layout.query.all()])


@api.route('/layouts/<int:id>', methods=['GET'])
@auth.login_required
def get_layout(id):
    layout = Layout.query.get(id)
    if layout:
        return jsonify(layout.as_dict())
    else:
        return make_response(jsonify({'error': 'layout not found'}), 404)


@api.route('/rooms/<string:name>/logs', methods=['GET'])
@auth.login_required
def get_room_logs(name):
    if not g.current_permissions.room_log_query:
        return make_response(jsonify({'error': 'insufficient rights'}), 403)

    room = Room.query.get(name)
    if room:
        return jsonify([log.as_dict() for log in room.logs])
    else:
        return make_response(jsonify({'error': 'room not found'}), 404)


@api.route('/users/<int:id>/logs', methods=['GET'])
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

    user = User.query.get(id)
    if user:
        return jsonify({room.name: list(filter_private_messages([log.as_dict() for log in room.logs], user.id))
                        for room in user.rooms})
    else:
        return make_response(jsonify({'error': 'user not found'}), 404)


@api.route('/users/<int:id>/task', methods=['GET'])
@auth.login_required
def get_user_task(id):
    user = User.query.get(id)
    if user:
        return jsonify(user.token.task.as_dict() if user.token.task else None)
    else:
        return make_response(jsonify({'error': 'user not found'}), 404)


@api.route('/users/<int:id>/logs', methods=['POST'])
@auth.login_required
def post_user_logs(id):
    if not g.current_permissions.user_log_event:
        return make_response(jsonify({'error': 'insufficient rights'}), 403)

    user = User.query.get(id)
    if not user:
        return make_response(jsonify({'error': 'user not found'}), 404)

    data = request.get_json(force=True) if request.is_json else None
    if not data:
        return make_response(jsonify({'error': 'bad request'}, 400))

    event = data.get('event')
    if not event:
        return make_response(jsonify({'error': 'missing parameter: `event`'}, 400))

    if 'room' in data:
        room = Room.query.get(data['room'])
        if not room:
            return make_response(jsonify({'error': 'room not found'}), 404)
    else:
        room = None

    try:
        return jsonify(log_event(event, user, room, data.get('data')).as_dict())
    except (IntegrityError, StatementError) as e:
        return make_response(jsonify({'error': str(e)}), 400)
