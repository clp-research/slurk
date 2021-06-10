from flask.views import MethodView
from flask.globals import current_app
from marshmallow_sqlalchemy.schema import SQLAlchemySchema, auto_field

from app.extensions.api import Blueprint
from app.models import User

from . import CommonSchema
from .tokens import TokenId


blp = Blueprint(User.__tablename__ + 's', __name__)


NAME_DESC = (
    'Name of the user',
    'Filter for a user name'
)
TOKEN_ID_DESC = (
    'Token associated with this user',
    'Filter for users using this token'
)
SESSION_ID_DESC = (
    'SocketIO session ID for this user',
    'Filter for a SocketIO session ID'
)


# Base schema used for creating a `Log`.
class UserSchema(CommonSchema, SQLAlchemySchema):
    class Meta:
        model = User

    name = auto_field(metadata={'description': NAME_DESC[0]})
    token_id = TokenId(required=True, load_only=True, metadata={'description': TOKEN_ID_DESC[0]})
    session_id = auto_field(dump_only=True, metadata={'description': SESSION_ID_DESC[0]})


# Same as `UserSchema` but Base schema but `required` set to false to prettify OpenAPI.
class UserResponseSchema(UserSchema):
    name = auto_field(required=False, metadata={'description': NAME_DESC[0]})


# Used for `PATCH`, which does not requires fields to be set
class UserUpdateSchema(UserSchema):
    name = auto_field(allow_none=True, required=False, metadata={'description': NAME_DESC[0]})
    token_id = TokenId(allow_none=True, metadata={'description': TOKEN_ID_DESC[0]})


# Same as `UserUpdateSchema` but with other descriptions to prettify OpenAPI.
class UserQuerySchema(UserUpdateSchema):
    name = auto_field(allow_none=True, required=False, metadata={'description': NAME_DESC[1]})
    token_id = TokenId(allow_none=True, metadata={'description': TOKEN_ID_DESC[1]})
    session_id = auto_field(metadata={'description': SESSION_ID_DESC[1]})


@blp.route('/')
class Users(MethodView):
    @blp.etag
    @blp.arguments(UserQuerySchema, location='query')
    @blp.response(200, UserResponseSchema(many=True))
    def get(self, args):
        """List users"""
        return UserQuerySchema().list(args)

    @blp.etag
    @blp.arguments(UserSchema)
    @blp.response(201, UserResponseSchema)
    @blp.login_required
    def post(self, item):
        """Add a new user"""
        return UserSchema().post(item)


@blp.route('/<int:user_id>')
class UserById(MethodView):
    @blp.etag
    @blp.query('user', UserSchema)
    @blp.response(200, UserResponseSchema)
    def get(self, *, user):
        """Get a user by ID"""
        return user

    @blp.etag
    @blp.query('user', UserSchema)
    @blp.arguments(UserSchema)
    @blp.response(200, UserResponseSchema)
    @blp.login_required
    def put(self, new_user, *, user):
        """Replace a user identified by ID"""
        return UserSchema().put(user, new_user)

    @blp.etag
    @blp.query('user', UserSchema)
    @blp.arguments(UserUpdateSchema)
    @blp.response(200, UserResponseSchema)
    @blp.login_required
    def patch(self, new_user, *, user):
        """Update a user identified by ID"""
        return UserUpdateSchema().patch(user, new_user)

    @blp.etag
    @blp.query('user', UserSchema)
    @blp.response(204)
    @blp.login_required
    def delete(self, *, user):
        """Delete a user identified by ID"""
        UserSchema().delete(user)
