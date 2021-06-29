from flask.views import MethodView
from flask.globals import current_app
from flask_smorest.error_handler import ErrorSchema
import marshmallow as ma

from app.extensions.api import Blueprint
from app.models import Token, Permissions, Room, Task
from app.views.api import CommonSchema, Id


blp = Blueprint(Token.__tablename__ + 's', __name__)


class TokenId(ma.fields.UUID):
    def _validated(self, value):
        id = str(super()._validated(value))
        if current_app.session.query(Token).get(id) is None:
            raise ma.ValidationError(f'Token `{id}` does not exist')
        return id


class TokenSchema(CommonSchema):
    class Meta:
        model = Token

    id = TokenId(
        dump_only=True,
        description='Unique ID that identifies this entity')
    permissions_id = Id(
        Permissions,
        required=True,
        description='Permissions for this token',
        filter_description='Filter for permissions')
    logins_left = ma.fields.Integer(
        missing=1,
        description='Logins left for this token',
        filter_description='Filter for left logins')
    task_id = Id(
        Task,
        missing=None,
        description='Task assigned to this token',
        filter_description='Filter for tasks')
    room_id = Id(
        Room,
        missing=None,
        description='Room assigned to this token',
        filter_description='Filter for rooms')


@blp.route('/')
class Tokens(MethodView):
    @blp.etag
    @blp.arguments(TokenSchema.Filter, location='query')
    @blp.response(200, TokenSchema.Response(many=True))
    @blp.login_required
    def get(self, args):
        """List tokens"""
        return TokenSchema().list(args)

    @blp.etag
    @blp.arguments(TokenSchema.Creation)
    @blp.response(201, TokenSchema.Response)
    @blp.login_required
    def post(self, item):
        """Add a new token"""
        return TokenSchema().post(item)


@blp.route('/<uuid:token_id>')
class TokensById(MethodView):
    @blp.query('token', TokenSchema)
    @blp.response(200, TokenSchema.Response)
    def get(self, *, token):
        """Get a token by ID"""
        return token

    @blp.etag
    @blp.query('token', TokenSchema)
    @blp.arguments(TokenSchema.Creation)
    @blp.response(200, TokenSchema.Response)
    @blp.login_required
    def put(self, new_token, *, token):
        """Replace a token identified by ID"""
        return TokenSchema().put(token, new_token)

    @blp.etag
    @blp.query('token', TokenSchema)
    @blp.arguments(TokenSchema.Update)
    @blp.response(200, TokenSchema.Response)
    @blp.login_required
    def patch(self, new_token, *, token):
        """Update a token identified by ID"""
        return TokenSchema().patch(token, new_token)

    @blp.etag
    @blp.query('token', TokenSchema)
    @blp.response(204)
    @blp.alt_response(422, ErrorSchema)
    @blp.login_required
    def delete(self, *, token):
        """Delete a token identified by ID"""
        TokenSchema().delete(token)
