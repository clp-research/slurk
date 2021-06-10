from flask.views import MethodView
from flask.globals import current_app
from marshmallow_sqlalchemy.schema import SQLAlchemySchema, auto_field
import marshmallow as ma

from app.extensions.api import Blueprint
from app.models import Token, Permissions, Room, Task

from . import CommonSchema, Id


blp = Blueprint(Token.__tablename__ + 's', __name__)


ID_DESC = (
    'Unique ID that identifies this entity',
)
PERMISSIONS_ID_DESC = (
    'Permissions for this token',
    'Filter for permissions'
)
TASK_ID_DESC = (
    'Task assigned to this token',
    'Filter for tasks'
)
ROOM_ID_DESC = (
    'Room assigned to this token',
    'Filter for rooms'
)
LOGINS_LEFT_DESC = (
    'Logins left for this token',
    'Filter for left logins'
)


class TokenId(ma.fields.UUID):
    def _validated(self, value):
        id = str(super()._validated(value))
        self.error_messages['foreign_key'] = f'Token `{id}` does not exist'
        if current_app.session.query(Token).get(id) is None:
            raise self.make_error('foreign_key')
        return id


def uuid():
    from uuid import uuid4
    return str(uuid4())


# Base schema used for creating a `Log`.
class TokenSchema(CommonSchema, SQLAlchemySchema):
    class Meta:
        model = Token

    id = TokenId(missing=uuid, dump_only=True, metadata={'description': ID_DESC[0]})
    permissions_id = Id(table=Permissions, required=True, metadata={'description': PERMISSIONS_ID_DESC[0]})
    logins_left = auto_field(missing=1, metadata={'description': LOGINS_LEFT_DESC[0]})
    task_id = Id(table=Task, allow_none=True, metadata={'description': TASK_ID_DESC[0]})
    room_id = Id(table=Room, allow_none=True, metadata={'description': ROOM_ID_DESC[0]})


# Same as `TokenSchema` but `required` set to false to prettify OpenAPI.
class TokenResponseSchema(TokenSchema):
    permissions_id = Id(table=Permissions, required=False, metadata={'description': PERMISSIONS_ID_DESC[0]})
    logins_left = auto_field(metadata={'description': LOGINS_LEFT_DESC[0]})


# Used for `PATCH`, which does not requires fields to be set
class TokenUpdateSchema(TokenSchema):
    permissions_id = Id(table=Permissions, required=False, allow_none=True,
                        metadata={'description': PERMISSIONS_ID_DESC[0]})
    logins_left = auto_field(allow_none=True, metadata={'description': LOGINS_LEFT_DESC[0]})


# Same as `TokenUpdateSchema` but with other descriptions to prettify OpenAPI.
class TokenQuerySchema(TokenUpdateSchema):
    permissions_id = Id(table=Permissions, allow_none=True, metadata={'description': PERMISSIONS_ID_DESC[1]})
    logins_left = auto_field(allow_none=True, metadata={'description': LOGINS_LEFT_DESC[1]})
    task_id = Id(table=Task, allow_none=True, metadata={'description': TASK_ID_DESC[1]})
    room_id = Id(table=Room, allow_none=True, metadata={'description': ROOM_ID_DESC[1]})


@blp.route('/')
class Tokens(MethodView):
    @blp.etag
    @blp.arguments(TokenQuerySchema, location='query')
    @blp.response(200, TokenResponseSchema(many=True))
    @blp.login_required
    def get(self, args):
        """List tokens"""
        return TokenQuerySchema().list(args)

    @blp.etag
    @blp.arguments(TokenSchema)
    @blp.response(201, TokenResponseSchema)
    @blp.login_required
    def post(self, item):
        """Add a new token"""
        return TokenSchema().post(item)


@blp.route('/<uuid:token_id>')
class TokensById(MethodView):
    @blp.query('token', TokenSchema)
    @blp.response(200, TokenResponseSchema)
    def get(self, *, token):
        """Get a token by ID"""
        return token

    @blp.etag
    @blp.query('token', TokenSchema)
    @blp.arguments(TokenSchema)
    @blp.response(200, TokenResponseSchema)
    @blp.login_required
    def put(self, new_token, *, token):
        """Replace a token identified by ID"""
        return TokenSchema().put(token, new_token)

    @blp.etag
    @blp.query('token', TokenSchema)
    @blp.arguments(TokenUpdateSchema)
    @blp.response(200, TokenResponseSchema)
    @blp.login_required
    def patch(self, new_token, *, token):
        """Update a token identified by ID"""
        return TokenUpdateSchema().patch(token, new_token)

    @blp.etag
    @blp.query('token', TokenSchema)
    @blp.response(204)
    @blp.login_required
    def delete(self, *, token):
        """Delete a token identified by ID"""
        TokenSchema().delete(token)
