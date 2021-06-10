from flask.views import MethodView
from flask.globals import current_app
from flask_smorest import abort
from http import HTTPStatus
from marshmallow_sqlalchemy.schema import SQLAlchemySchema
from sqlalchemy.sql.elements import or_
import marshmallow as ma

from app.extensions.api import Blueprint
from app.extensions.events import socketio
from app.models import Room, Layout, Log

from .users import UserSchema, UserResponseSchema, blp as user_blp
from .logs import LogResponseSchema
from . import CommonSchema, Id


blp = Blueprint(Room.__tablename__ + 's', __name__)


LAYOUT_ID_DESC = (
    'Layout for this room',
    'Filter for layout used in the rooms'
)


# Base schema used for creating a `Log`.
class RoomSchema(CommonSchema, SQLAlchemySchema):
    class Meta:
        model = Room

    layout_id = Id(table=Layout, required=True, metadata={'description': LAYOUT_ID_DESC[0]})


# Same as `RoomSchema` but Base schema but `required` set to false to prettify OpenAPI.
class RoomResponseSchema(RoomSchema):
    layout_id = Id(table=Layout, metadata={'description': LAYOUT_ID_DESC[0]})


# Used for `PATCH`, which does not requires fields to be set
class RoomUpdateSchema(RoomSchema):
    layout_id = Id(table=Layout, allow_none=True, metadata={'description': LAYOUT_ID_DESC[0]})


# Same as `RoomUpdateSchema` but with other descriptions to prettify OpenAPI.
class RoomQuerySchema(RoomUpdateSchema):
    layout_id = Id(table=Layout, allow_none=True, metadata={'description': LAYOUT_ID_DESC[1]})


@blp.route('/')
class Rooms(MethodView):
    @blp.etag
    @blp.arguments(RoomQuerySchema, location='query')
    @blp.response(200, RoomResponseSchema(many=True))
    def get(self, args):
        """List rooms"""
        return RoomQuerySchema().list(args)

    @blp.etag
    @blp.arguments(RoomSchema)
    @blp.response(201, RoomResponseSchema)
    @blp.login_required
    def post(self, item):
        """Add a new room"""
        return RoomSchema().post(item)


@blp.route('/<int:room_id>')
class RoomById(MethodView):
    @blp.etag
    @blp.query('room', RoomSchema)
    @blp.response(200, RoomResponseSchema)
    def get(self, *, room):
        """Get a room by ID"""
        return room

    @blp.etag
    @blp.query('room', RoomSchema)
    @blp.arguments(RoomSchema)
    @blp.response(200, RoomResponseSchema)
    @blp.login_required
    def put(self, new_room, *, room):
        """Replace a room identified by ID"""
        return RoomSchema().put(room, new_room)

    @blp.etag
    @blp.query('room', RoomSchema)
    @blp.arguments(RoomUpdateSchema)
    @blp.response(200, RoomResponseSchema)
    @blp.login_required
    def patch(self, new_room, *, room):
        """Update a room identified by ID"""
        return RoomUpdateSchema().patch(room, new_room)

    @blp.etag
    @blp.query('room', RoomSchema)
    @blp.response(204)
    @blp.login_required
    def delete(self, *, room):
        """Delete a room identified by ID"""
        RoomSchema().delete(room)


@blp.route('/<int:room_id>/users')
class UsersByRoomById(MethodView):
    @blp.etag
    @blp.query('room', RoomSchema)
    @blp.response(200, UserResponseSchema(many=True))
    def get(self, *, room):
        """List active users by rooms"""
        return filter(lambda u: u.session_id is not None, room.users)


# Note: user_blp. Required here as otherwise we would have circular dependencies
@user_blp.route('/<int:user_id>/rooms')
class RoomsByUserById(MethodView):
    @blp.etag
    @blp.query('user', UserSchema)
    @blp.response(200, RoomResponseSchema(many=True))
    def get(self, *, user):
        """List rooms by users"""
        return user.rooms


# Note: user_blp. Required here as otherwise we would have circular dependencies
@user_blp.route('/<int:user_id>/rooms/<int:room_id>')
class UserRoom(MethodView):
    @blp.etag
    @blp.query('user', UserSchema)
    @blp.query('room', RoomSchema)
    @blp.response(201, UserResponseSchema)
    @blp.login_required
    def post(self, *, user, room):
        """Add a user to a room"""
        user.join_room(room)
        return user

    @blp.etag
    @blp.query('user', UserSchema)
    @blp.query('room', RoomSchema, check_etag=False)
    @blp.response(204)
    @blp.login_required
    def delete(self, *, user, room):
        """Remove a user from a room"""
        user.leave_room(room)


@blp.route('/<int:room_id>/users/<int:user_id>/logs')
class LogsByUserByRoomById(MethodView):
    @blp.etag
    @blp.query('room', RoomSchema)
    @blp.query('user', UserSchema)
    @blp.response(200, LogResponseSchema(many=True))
    def get(self, *, room, user):
        """List logs by room and user"""
        return current_app.session.query(Log) \
            .filter_by(room_id=room.id) \
            .filter(or_(Log.receiver_id == None, Log.user_id == user.id, Log.receiver_id == user.id)) \
            .order_by(Log.date_created.asc()) \
            .all()  # NOQA


class AttributeSchema(ma.Schema):
    attribute = ma.fields.Str(required=True, metadata={'description': 'The attribute to be updated'})
    value = ma.fields.Str(required=True, metadata={'description': 'The value to be set for the given attribute'})


class TextSchema(ma.Schema):
    text = ma.fields.Str(required=True, metadata={'description': 'The text to be set for the given ID'})


class ClassSchema(ma.Schema):
    cls = ma.fields.Str(required=True, attribute='class', data_key='class',
                        metadata={'description': 'The class to be modified'})


@blp.route('/<int:room_id>/attribute/id/<string:id>')
class AttributeId(MethodView):
    @blp.query('room', RoomSchema, check_etag=False)
    @blp.arguments(AttributeSchema, as_kwargs=True)
    @blp.response(204)
    @blp.login_required
    def patch(self, *, room, id, **kwargs):
        """ Update an element identified by it's ID """
        kwargs['id'] = id
        Log.add("set_attribute", room=room, data=kwargs)
        socketio.emit('attribute_update', kwargs, room=str(room.id))
        return kwargs


# Note: user_blp. Required here as otherwise we would have circular dependencies
@user_blp.route('/<int:user_id>/attribute/id/<string:id>')
class AttributeId(MethodView):
    @blp.query('user', UserSchema, check_etag=False)
    @blp.arguments(AttributeSchema, as_kwargs=True)
    @blp.response(204)
    @blp.login_required
    def patch(self, *, user, id, **kwargs):
        """ Update an element identified by it's ID """
        kwargs['id'] = id
        Log.add("set_attribute", user=user, data=kwargs)
        if user.session_id is None:
            abort(HTTPStatus.UNPROCESSABLE_ENTITY, errors=dict(query={
                'user_id': f'User `{user.id} does not have a session id associated'
            }))
        socketio.emit('attribute_update', kwargs, room=user.session_id)
        return kwargs


@blp.route('/<int:room_id>/attribute/class/<string:cls>')
class AttributeClass(MethodView):
    @blp.query('room', RoomSchema, check_etag=False)
    @blp.arguments(AttributeSchema, as_kwargs=True)
    @blp.response(204)
    @blp.login_required
    def patch(self, *, room, cls, **kwargs):
        """ Update an element identified by it's class """
        kwargs['cls'] = cls
        Log.add("set_attribute", room=room, data=kwargs)
        socketio.emit('attribute_update', kwargs, room=str(room.id))
        return kwargs


# Note: user_blp. Required here as otherwise we would have circular dependencies
@user_blp.route('/<int:user_id>/attribute/class/<string:cls>')
class AttributeClass(MethodView):
    @blp.query('user', UserSchema, check_etag=False)
    @blp.arguments(AttributeSchema, as_kwargs=True)
    @blp.response(204)
    @blp.login_required
    def patch(self, *, user, cls, **kwargs):
        """ Update an element identified by it's class """
        kwargs['cls'] = cls
        Log.add("set_attribute", user=user, data=kwargs)
        if user.session_id is None:
            abort(HTTPStatus.UNPROCESSABLE_ENTITY, errors=dict(query={
                'user_id': f'User `{user.id} does not have a session id associated'
            }))
        socketio.emit('attribute_update', kwargs, room=user.session_id)
        return kwargs


@blp.route('/<int:room_id>/attribute/element/<string:element>')
class AttributeElement(MethodView):
    @blp.query('room', RoomSchema, check_etag=False)
    @blp.arguments(AttributeSchema, as_kwargs=True)
    @blp.response(204)
    @blp.login_required
    def patch(self, *, room, element, **kwargs):
        """ Update an element identified by it's type """
        kwargs['element'] = element
        Log.add("set_attribute", room=room, data=kwargs)
        socketio.emit('attribute_update', kwargs, room=str(room.id))
        return kwargs


# Note: user_blp. Required here as otherwise we would have circular dependencies
@user_blp.route('/<int:user_id>/attribute/element/<string:element>')
class AttributeElement(MethodView):
    @blp.query('user', UserSchema, check_etag=False)
    @blp.arguments(AttributeSchema, as_kwargs=True)
    @blp.response(204)
    @blp.login_required
    def patch(self, *, user, element, **kwargs):
        """ Update an element identified by it's type """
        kwargs['element'] = element
        Log.add("set_attribute", user=user, data=kwargs)
        if user.session_id is None:
            abort(HTTPStatus.UNPROCESSABLE_ENTITY, errors=dict(query={
                'user_id': f'User `{user.id} does not have a session id associated'
            }))
        socketio.emit('attribute_update', kwargs, room=user.session_id)
        return kwargs


@blp.route('/<int:room_id>/text/<string:id>')
class Text(MethodView):
    @blp.query('room', RoomSchema, check_etag=False)
    @blp.arguments(TextSchema, as_kwargs=True)
    @blp.response(204)
    @blp.login_required
    def patch(self, *, room, id, **kwargs):
        """ Update the text of an element identified by it's ID """
        kwargs['id'] = id
        Log.add("set_text", room=room, data=kwargs)
        socketio.emit('text_update', kwargs, room=str(room.id))
        return kwargs


# Note: user_blp. Required here as otherwise we would have circular dependencies
@user_blp.route('/<int:user_id>/text/<string:id>')
class Text(MethodView):
    @blp.query('user', UserSchema, check_etag=False)
    @blp.arguments(TextSchema, as_kwargs=True)
    @blp.response(204)
    @blp.login_required
    def patch(self, *, user, id, **kwargs):
        """ Update the text of an element identified by it's ID """
        kwargs['id'] = id
        Log.add("set_text", user=user, data=kwargs)
        if user.session_id is None:
            abort(HTTPStatus.UNPROCESSABLE_ENTITY, errors=dict(query={
                'user_id': f'User `{user.id} does not have a session id associated'
            }))
        socketio.emit('text_update', kwargs, room=str(user.session_id))
        return kwargs


@blp.route('/<int:room_id>/class/<string:id>')
class Class(MethodView):
    @blp.query('room', RoomSchema, check_etag=False)
    @blp.arguments(ClassSchema, as_kwargs=True)
    @blp.response(204)
    @blp.login_required
    def post(self, *, room, id, **kwargs):
        """ Add a class to an element identified by it's ID """
        kwargs['id'] = id
        Log.add("class_add", room=room, data=kwargs)
        socketio.emit('class_add', kwargs, room=str(room.id))
        return kwargs

    @blp.query('room', RoomSchema, check_etag=False)
    @blp.arguments(ClassSchema, as_kwargs=True)
    @blp.response(204)
    @blp.login_required
    def delete(self, *, room, id, **kwargs):
        """ Remove a class from an element identified by it's ID """
        kwargs['id'] = id
        Log.add("class_remove", room=room, data=kwargs)
        socketio.emit('class_remove', kwargs, room=str(room.id))
        return kwargs


# Note: user_blp. Required here as otherwise we would have circular dependencies
@user_blp.route('/<int:user_id>/class/<string:id>')
class Class(MethodView):
    @blp.query('user', UserSchema, check_etag=False)
    @blp.arguments(ClassSchema, as_kwargs=True)
    @blp.response(204)
    @blp.login_required
    def post(self, *, user, id, **kwargs):
        """ Add a class to an element identified by it's ID """
        kwargs['id'] = id
        Log.add("class_add", user=user, data=kwargs)
        if user.session_id is None:
            abort(HTTPStatus.UNPROCESSABLE_ENTITY, errors=dict(query={
                'user_id': f'User `{user.id} does not have a session id associated'
            }))
        socketio.emit('class_add', kwargs, room=str(user.session_id))
        return kwargs

    @blp.query('user', UserSchema, check_etag=False)
    @blp.arguments(ClassSchema, as_kwargs=True)
    @blp.response(204)
    @blp.login_required
    def delete(self, *, user, id, **kwargs):
        """ Remove a class from an element identified by it's ID """
        kwargs['id'] = id
        Log.add("class_remove", user=user, data=kwargs)
        if user.session_id is None:
            abort(HTTPStatus.UNPROCESSABLE_ENTITY, errors=dict(query={
                'user_id': f'User `{user.id} does not have a session id associated'
            }))
        socketio.emit('class_remove', kwargs, room=str(user.session_id))
        return kwargs
