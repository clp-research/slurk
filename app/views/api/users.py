from flask.views import MethodView
import marshmallow as ma

from app.extensions.api import Blueprint
from app.models import User

from . import CommonSchema
from .tokens import TokenId


blp = Blueprint(User.__tablename__ + 's', __name__)


class UserSchema(CommonSchema):
    class Meta:
        model = User

    name = ma.fields.String(required=True, description='Name of the user', filter_description='Filter for a user name')
    token_id = TokenId(
        required=True,
        load_only=True,
        description='Token associated with this user',
        filter_description='Filter for users using this token')
    session_id = ma.fields.String(dump_only=True,
                                  description='SocketIO session ID for this user',
                                  filter_description='Filter for a SocketIO session ID')


UserCreationSchema = UserSchema().creation_schema
UserUpdateSchema = UserSchema().update_schema
UserResponseSchema = UserSchema().response_schema
UserQuerySchema = UserSchema().query_schema


@blp.route('/')
class Users(MethodView):
    @blp.etag
    @blp.arguments(UserQuerySchema, location='query')
    @blp.response(200, UserResponseSchema(many=True))
    def get(self, args):
        """List users"""
        return UserSchema().list(args)

    @blp.etag
    @blp.arguments(UserCreationSchema)
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
    @blp.arguments(UserCreationSchema)
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
