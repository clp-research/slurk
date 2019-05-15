from sqlalchemy.exc import StatementError, IntegrityError

from .layout import *
from .room import *
from .token import *
from .user import *
from .task import *


from flask import Blueprint, request


api = Blueprint('api', __name__, url_prefix="/api/v2/")


@api.route('/rooms', methods=['GET'])
@login_required
def get_rooms():
    if not current_user.get_id():
        return make_response(jsonify({'error': 'invalid session'}), 403)
    if not current_user.token.permissions.room_query:
        return make_response(jsonify({'error': 'insufficient rights'}), 401)

    return jsonify([dict(uri="/rooms/"+room.name, **room.as_dict()) for room in Room.query.all()])


@api.route('/rooms/<string:name>', methods=['GET'])
@login_required
def get_room(name):
    if not current_user.get_id():
        return make_response(jsonify({'error': 'invalid session'}), 403)
    if not current_user.token.permissions.room_query:
        return make_response(jsonify({'error': 'insufficient rights'}), 401)

    room = Room.query.get(name)
    if room:
        return jsonify({'room': room.as_dict()})
    else:
        return make_response(jsonify({'error': 'Not found'}), 404)


@api.route('/rooms', methods=['POST'])
@login_required
def post_rooms():
    if not current_user.get_id():
        return make_response(jsonify({'error': 'invalid session'}), 403)
    if not current_user.token.permissions.room_create:
        return make_response(jsonify({'error': 'insufficient rights'}), 401)

    data = request.get_json(force=True) if request.is_json else None
    if not data:
        return make_response(jsonify({'error': 'bad request'}, 400))

    name = data.get('name')
    label = data.get('label')
    if not name:
        return make_response(jsonify({'error': 'missing parameter: `name`'}, 400))
    if not label:
        return make_response(jsonify({'error': 'missing parameter: `label`'}, 400))

    if 'layout' in data:
        layout = Layout.query.get(data['layout'])
        if not layout:
            return make_response(jsonify({'error': 'invalid layout'}), 404)
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
        return jsonify({'room': room.as_dict()})
    except (IntegrityError, StatementError) as e:
        return make_response(jsonify({'error': str(e)}), 400)


@api.route('/rooms/<string:name>', methods=['PUT'])
@login_required
def put_rooms(name):
    if not current_user.get_id():
        return make_response(jsonify({'error': 'invalid session'}), 403)
    if not current_user.token.permissions.room_update:
        return make_response(jsonify({'error': 'insufficient rights'}), 401)

    data = request.get_json(force=True) if request.is_json else None
    if not data:
        return make_response(jsonify({'error': 'bad request'}, 400))

    room = Room.query.get(name)
    if not room:
        return make_response(jsonify({'error': 'Not found'}), 404)

    try:
        if 'label' in data:
            room.label = data['label']
        if 'layout' in data:
            layout = Layout.query.get(data['layout'])
            if not layout:
                return make_response(jsonify({'error': 'invalid layout'}), 404)
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
        return jsonify({'room': room.as_dict()})
    except (IntegrityError, StatementError) as e:
        return make_response(jsonify({'error': str(e)}), 400)


@api.route('/rooms/<string:name>', methods=['DELETE'])
@login_required
def delete_rooms(name):
    if not current_user.get_id():
        return make_response(jsonify({'error': 'invalid session'}), 403)
    if not current_user.token.permissions.room_delete:
        return make_response(jsonify({'error': 'insufficient rights'}), 401)

    room = Room.query.get(name)
    if not room:
        return make_response(jsonify({'error': 'Not found'}), 404)

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
