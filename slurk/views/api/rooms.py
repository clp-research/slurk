from flask.views import MethodView
from flask.globals import current_app
from flask_smorest import abort
from flask_smorest.error_handler import ErrorSchema
from http import HTTPStatus
from sqlalchemy.sql.elements import or_
import marshmallow as ma

from slurk.extensions.api import Blueprint
from slurk.extensions.events import socketio
from slurk.models import Room, Layout, Log
from slurk.views.api.openvidu.fields import SessionId as OpenViduSessionId

from .users import UserSchema, blp as user_blp
from .logs import LogSchema
from . import CommonSchema, Id


blp = Blueprint(Room.__tablename__ + "s", __name__)


class RoomSchema(CommonSchema):
    class Meta:
        model = Room

    layout_id = Id(
        Layout,
        required=True,
        description="Layout for this room",
        filter_description="Filter for layout used in the rooms",
    )
    openvidu_session_id = OpenViduSessionId(
        description="Session for OpenVidu",
        filter_description="Filter for an OpenVidu session",
    )


@blp.route("/")
class Rooms(MethodView):
    @blp.etag
    @blp.arguments(RoomSchema.Filter, location="query")
    @blp.response(200, RoomSchema.Response(many=True))
    def get(self, args):
        """List rooms"""
        return RoomSchema().list(args)

    @blp.etag
    @blp.arguments(RoomSchema.Creation)
    @blp.response(201, RoomSchema.Response)
    @blp.login_required
    def post(self, item):
        """Add a new room"""
        return RoomSchema().post(item)


@blp.route("/<int:room_id>")
class RoomById(MethodView):
    @blp.etag
    @blp.query("room", RoomSchema)
    @blp.response(200, RoomSchema.Response)
    def get(self, *, room):
        """Get a room by ID"""
        return room

    @blp.etag
    @blp.query("room", RoomSchema)
    @blp.arguments(RoomSchema.Creation)
    @blp.response(200, RoomSchema.Response)
    @blp.login_required
    def put(self, new_room, *, room):
        """Replace a room identified by ID"""
        return RoomSchema().put(room, new_room)

    @blp.etag
    @blp.query("room", RoomSchema)
    @blp.arguments(RoomSchema.Update)
    @blp.response(200, RoomSchema.Response)
    @blp.login_required
    def patch(self, new_room, *, room):
        """Update a room identified by ID"""
        return RoomSchema().patch(room, new_room)

    @blp.etag
    @blp.query("room", RoomSchema)
    @blp.response(204)
    @blp.alt_response(422, ErrorSchema)
    @blp.login_required
    def delete(self, *, room):
        """Delete a room identified by ID"""
        RoomSchema().delete(room)


@blp.route("/<int:room_id>/users")
class UsersByRoomById(MethodView):
    @blp.etag
    @blp.query("room", RoomSchema)
    @blp.response(200, UserSchema.Response(many=True))
    def get(self, *, room):
        """List active users by rooms"""
        return filter(lambda u: u.session_id is not None, room.users)


# Note: user_blp. Required here as otherwise we would have circular dependencies
@user_blp.route("/<int:user_id>/rooms")
class RoomsByUserById(MethodView):
    @blp.etag
    @blp.query("user", UserSchema)
    @blp.response(200, RoomSchema.Response(many=True))
    def get(self, *, user):
        """List rooms by users"""
        return user.rooms


# Note: user_blp. Required here as otherwise we would have circular dependencies
@user_blp.route("/<int:user_id>/rooms/<int:room_id>")
class UserRoom(MethodView):
    @blp.etag
    @blp.query("user", UserSchema)
    @blp.query("room", RoomSchema)
    @blp.response(201, UserSchema.Response)
    @blp.login_required
    def post(self, *, user, room):
        """Add a user to a room"""
        user.join_room(room)
        return user

    @blp.etag
    @blp.query("user", UserSchema)
    @blp.query("room", RoomSchema, check_etag=False)
    @blp.response(204)
    @blp.login_required
    def delete(self, *, user, room):
        """Remove a user from a room"""
        user.leave_room(room)


@blp.route("/<int:room_id>/users/<int:user_id>/logs")
class LogsByUserByRoomById(MethodView):
    @blp.etag
    @blp.query("room", RoomSchema)
    @blp.query("user", UserSchema)
    @blp.response(200, LogSchema.Response(many=True))
    def get(self, *, room, user):
        """List logs by room and user"""
        return (
            current_app.session.query(Log)
            .filter_by(room_id=room.id)
            .filter(
                or_(
                    Log.receiver_id == None,  # NOQA
                    Log.user_id == user.id,
                    Log.receiver_id == user.id,
                )
            )
            .order_by(Log.date_created.asc())
            .all()
        )


class AttributeSchema(ma.Schema):
    attribute = ma.fields.Str(
        required=True, metadata={"description": "The attribute to be updated"}
    )
    value = ma.fields.Str(
        required=True,
        metadata={"description": "The value to be set for the given attribute"},
    )


class TextSchema(ma.Schema):
    text = ma.fields.Str(
        required=True, metadata={"description": "The text to be set for the given ID"}
    )


class ClassSchema(ma.Schema):
    cls = ma.fields.Str(
        required=True,
        attribute="class",
        data_key="class",
        metadata={"description": "The class to be modified"},
    )


@blp.route("/<int:room_id>/attribute/id/<string:id>")
class AttributeId(MethodView):
    @blp.query("room", RoomSchema, check_etag=False)
    @blp.arguments(AttributeSchema, as_kwargs=True)
    @blp.response(204)
    @blp.login_required
    def patch(self, *, room, id, **kwargs):
        """Update an element identified by it's ID"""
        kwargs["id"] = id
        Log.add("set_attribute", room=room, data=kwargs)
        socketio.emit("attribute_update", kwargs, room=str(room.id))
        return kwargs


# Note: user_blp. Required here as otherwise we would have circular dependencies
@user_blp.route("/<int:user_id>/attribute/id/<string:id>")
class UserAttributeId(MethodView):
    @blp.query("user", UserSchema, check_etag=False)
    @blp.arguments(AttributeSchema, as_kwargs=True)
    @blp.response(204)
    @blp.login_required
    def patch(self, *, user, id, **kwargs):
        """Update an element identified by it's ID"""
        kwargs["id"] = id
        Log.add("set_attribute", user=user, data=kwargs)
        if user.session_id is None:
            abort(
                HTTPStatus.UNPROCESSABLE_ENTITY,
                query={
                    "user_id": f"User `{user.id} does not have a session id associated"
                },
            )
        socketio.emit("attribute_update", kwargs, room=user.session_id)
        return kwargs


@blp.route("/<int:room_id>/attribute/class/<string:cls>")
class AttributeClass(MethodView):
    @blp.query("room", RoomSchema, check_etag=False)
    @blp.arguments(AttributeSchema, as_kwargs=True)
    @blp.response(204)
    @blp.login_required
    def patch(self, *, room, cls, **kwargs):
        """Update an element identified by it's class"""
        kwargs["cls"] = cls
        Log.add("set_attribute", room=room, data=kwargs)
        socketio.emit("attribute_update", kwargs, room=str(room.id))
        return kwargs


# Note: user_blp. Required here as otherwise we would have circular dependencies
@user_blp.route("/<int:user_id>/attribute/class/<string:cls>")
class UserAttributeClass(MethodView):
    @blp.query("user", UserSchema, check_etag=False)
    @blp.arguments(AttributeSchema, as_kwargs=True)
    @blp.response(204)
    @blp.login_required
    def patch(self, *, user, cls, **kwargs):
        """Update an element identified by it's class"""
        kwargs["cls"] = cls
        Log.add("set_attribute", user=user, data=kwargs)
        if user.session_id is None:
            abort(
                HTTPStatus.UNPROCESSABLE_ENTITY,
                query={
                    "user_id": f"User `{user.id} does not have a session id associated"
                },
            )
        socketio.emit("attribute_update", kwargs, room=user.session_id)
        return kwargs


@blp.route("/<int:room_id>/attribute/element/<string:element>")
class AttributeElement(MethodView):
    @blp.query("room", RoomSchema, check_etag=False)
    @blp.arguments(AttributeSchema, as_kwargs=True)
    @blp.response(204)
    @blp.login_required
    def patch(self, *, room, element, **kwargs):
        """Update an element identified by it's type"""
        kwargs["element"] = element
        Log.add("set_attribute", room=room, data=kwargs)
        socketio.emit("attribute_update", kwargs, room=str(room.id))
        return kwargs


# Note: user_blp. Required here as otherwise we would have circular dependencies
@user_blp.route("/<int:user_id>/attribute/element/<string:element>")
class UserAttributeElement(MethodView):
    @blp.query("user", UserSchema, check_etag=False)
    @blp.arguments(AttributeSchema, as_kwargs=True)
    @blp.response(204)
    @blp.login_required
    def patch(self, *, user, element, **kwargs):
        """Update an element identified by it's type"""
        kwargs["element"] = element
        Log.add("set_attribute", user=user, data=kwargs)
        if user.session_id is None:
            abort(
                HTTPStatus.UNPROCESSABLE_ENTITY,
                query={
                    "user_id": f"User `{user.id} does not have a session id associated"
                },
            )
        socketio.emit("attribute_update", kwargs, room=user.session_id)
        return kwargs


@blp.route("/<int:room_id>/text/<string:id>")
class Text(MethodView):
    @blp.query("room", RoomSchema, check_etag=False)
    @blp.arguments(TextSchema, as_kwargs=True)
    @blp.response(204)
    @blp.login_required
    def patch(self, *, room, id, **kwargs):
        """Update the text of an element identified by it's ID"""
        kwargs["id"] = id
        Log.add("set_text", room=room, data=kwargs)
        socketio.emit("text_update", kwargs, room=str(room.id))
        return kwargs


# Note: user_blp. Required here as otherwise we would have circular dependencies
@user_blp.route("/<int:user_id>/text/<string:id>")
class UserText(MethodView):
    @blp.query("user", UserSchema, check_etag=False)
    @blp.arguments(TextSchema, as_kwargs=True)
    @blp.response(204)
    @blp.login_required
    def patch(self, *, user, id, **kwargs):
        """Update the text of an element identified by it's ID"""
        kwargs["id"] = id
        Log.add("set_text", user=user, data=kwargs)
        if user.session_id is None:
            abort(
                HTTPStatus.UNPROCESSABLE_ENTITY,
                query={
                    "user_id": f"User `{user.id} does not have a session id associated"
                },
            )
        socketio.emit("text_update", kwargs, room=str(user.session_id))
        return kwargs


@blp.route("/<int:room_id>/class/<string:id>")
class Class(MethodView):
    @blp.query("room", RoomSchema, check_etag=False)
    @blp.arguments(ClassSchema, as_kwargs=True)
    @blp.response(204)
    @blp.login_required
    def post(self, *, room, id, **kwargs):
        """Add a class to an element identified by it's ID"""
        kwargs["id"] = id
        Log.add("class_add", room=room, data=kwargs)
        socketio.emit("class_add", kwargs, room=str(room.id))
        return kwargs

    @blp.query("room", RoomSchema, check_etag=False)
    @blp.arguments(ClassSchema, as_kwargs=True)
    @blp.response(204)
    @blp.login_required
    def delete(self, *, room, id, **kwargs):
        """Remove a class from an element identified by it's ID"""
        kwargs["id"] = id
        Log.add("class_remove", room=room, data=kwargs)
        socketio.emit("class_remove", kwargs, room=str(room.id))
        return kwargs


# Note: user_blp. Required here as otherwise we would have circular dependencies
@user_blp.route("/<int:user_id>/class/<string:id>")
class UserClass(MethodView):
    @blp.query("user", UserSchema, check_etag=False)
    @blp.arguments(ClassSchema, as_kwargs=True)
    @blp.response(204)
    @blp.login_required
    def post(self, *, user, id, **kwargs):
        """Add a class to an element identified by it's ID"""
        kwargs["id"] = id
        Log.add("class_add", user=user, data=kwargs)
        if user.session_id is None:
            abort(
                HTTPStatus.UNPROCESSABLE_ENTITY,
                query={
                    "user_id": f"User `{user.id} does not have a session id associated"
                },
            )
        socketio.emit("class_add", kwargs, room=str(user.session_id))
        return kwargs

    @blp.query("user", UserSchema, check_etag=False)
    @blp.arguments(ClassSchema, as_kwargs=True)
    @blp.response(204)
    @blp.login_required
    def delete(self, *, user, id, **kwargs):
        """Remove a class from an element identified by it's ID"""
        kwargs["id"] = id
        Log.add("class_remove", user=user, data=kwargs)
        if user.session_id is None:
            abort(
                HTTPStatus.UNPROCESSABLE_ENTITY,
                query={
                    "user_id": f"User `{user.id} does not have a session id associated"
                },
            )
        socketio.emit("class_remove", kwargs, room=str(user.session_id))
        return kwargs
