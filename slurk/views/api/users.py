from flask.views import MethodView
from flask.globals import current_app
from flask_smorest.error_handler import ErrorSchema
from werkzeug.exceptions import UnprocessableEntity
import marshmallow as ma

from slurk.extensions.api import Blueprint, abort
from slurk.models import User, Task, Token

from . import CommonSchema
from .tasks import TaskSchema
from .tokens import TokenId


blp = Blueprint(User.__tablename__ + "s", __name__)


class UserSchema(CommonSchema):
    class Meta:
        model = User

    name = ma.fields.String(
        required=True,
        description="Name of the user",
        filter_description="Filter for a user name",
    )
    token_id = TokenId(
        load_only=True,
        required=True,
        description="Token associated with this user",
        filter_description="Filter for users using this token",
    )
    session_id = ma.fields.String(
        dump_only=True,
        description="SocketIO session ID for this user",
        filter_description="Filter for a SocketIO session ID",
    )


@blp.route("/")
class Users(MethodView):
    @blp.etag
    @blp.arguments(UserSchema.Filter, location="query")
    @blp.response(200, UserSchema.Response(many=True))
    def get(self, args):
        """List users"""
        return UserSchema().list(args)

    @blp.etag
    @blp.arguments(UserSchema.Creation)
    @blp.response(201, UserSchema.Response)
    @blp.login_required
    def post(self, item):
        """Add a new user

        The token is required to have registrations left and a room associated"""

        db = current_app.session
        token = db.query(Token).get(item["token_id"])

        try:
            token.add_user(db)
        except ValueError as e:
            abort(
                UnprocessableEntity,
                json=dict(token_id=str(e)),
            )

        user = UserSchema().post(item)
        user.rooms = [token.room]
        db.commit()
        return user


@blp.route("/<int:user_id>")
class UserById(MethodView):
    @blp.etag
    @blp.query("user", UserSchema)
    @blp.response(200, UserSchema.Response)
    def get(self, *, user):
        """Get a user by ID"""
        return user

    @blp.etag
    @blp.query("user", UserSchema)
    @blp.arguments(UserSchema.Creation)
    @blp.response(200, UserSchema.Response)
    @blp.login_required
    def put(self, new_user, *, user):
        """Replace a user identified by ID"""
        db = current_app.session
        token = db.query(Token).get(new_user["token_id"])

        try:
            token.add_user(db)
        except ValueError as e:
            abort(
                UnprocessableEntity,
                json=dict(token_id=str(e)),
            )
        return UserSchema().put(user, new_user)

    @blp.etag
    @blp.query("user", UserSchema)
    @blp.arguments(UserSchema.Update)
    @blp.response(200, UserSchema.Response)
    @blp.login_required
    def patch(self, new_user, *, user):
        """Update a user identified by ID"""
        token_id = new_user.get("token_id")

        if token_id is not None:
            db = current_app.session
            token = db.query(Token).get(token_id)

            try:
                token.add_user(db)
            except ValueError as e:
                abort(
                    UnprocessableEntity,
                    json=dict(token_id=str(e)),
                )
        return UserSchema().patch(user, new_user)

    @blp.etag
    @blp.query("user", UserSchema)
    @blp.response(204)
    @blp.alt_response(422, ErrorSchema)
    @blp.login_required
    def delete(self, *, user):
        """Delete a user identified by ID"""
        UserSchema().delete(user)


@blp.route("/<int:user_id>/task")
class TaskByUserById(MethodView):
    @blp.etag
    @blp.query("user", UserSchema)
    @blp.response(200, TaskSchema.Response)
    def get(self, *, user):
        task_id = user.token.task_id
        if task_id is not None:
            task = current_app.session.query(Task).get(task_id)
            return task
