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

# Only two schemas are needed but four are used to prettify OpenAPI Documentation


class TokenSchema(CommonSchema, SQLAlchemySchema):
    class Meta:
        model = Token

    id = TokenId(missing=uuid, dump_only=True, metadata={'description': ID_DESC[0]})
    permissions_id = Id(table=Permissions, required=True, metadata={'description': PERMISSIONS_ID_DESC[0]})
    logins_left = auto_field(missing=1, metadata={'description': LOGINS_LEFT_DESC[0]})
    task_id = Id(table=Task, allow_none=True, metadata={'description': TASK_ID_DESC[0]})
    room_id = Id(table=Room, allow_none=True, metadata={'description': ROOM_ID_DESC[0]})


class TokenResponseSchema(TokenSchema):
    permissions_id = Id(table=Permissions, required=False, metadata={'description': PERMISSIONS_ID_DESC[0]})
    logins_left = auto_field(metadata={'description': LOGINS_LEFT_DESC[0]})


class TokenUpdateSchema(TokenSchema):
    permissions_id = Id(table=Permissions, required=False, allow_none=True,
                        metadata={'description': PERMISSIONS_ID_DESC[0]})
    logins_left = auto_field(allow_none=True, metadata={'description': LOGINS_LEFT_DESC[0]})


class TokenQuerySchema(TokenSchema):
    permissions_id = Id(table=Permissions, allow_none=True, metadata={'description': PERMISSIONS_ID_DESC[1]})
    logins_left = auto_field(allow_none=True, metadata={'description': LOGINS_LEFT_DESC[1]})
    task_id = Id(table=Task, allow_none=True, metadata={'description': TASK_ID_DESC[1]})
    room_id = Id(table=Room, allow_none=True, metadata={'description': ROOM_ID_DESC[1]})


@blp.route('/')
class Tokens(MethodView):
    @blp.etag
    @blp.arguments(TokenQuerySchema, location='query')
    @blp.response(200, TokenResponseSchema(many=True))
    @blp.paginate()
    @blp.login_required
    def get(self, args, pagination_parameters):
        """List tokens"""
        db = current_app.session
        query = db.query(Token) \
            .filter_by(**args) \
            .order_by(Token.date_created.desc())
        pagination_parameters.item_count = query.count()
        return query \
            .limit(pagination_parameters.page_size) \
            .offset(pagination_parameters.first_item) \
            .all()

    @blp.etag
    @blp.arguments(TokenSchema)
    @blp.response(201, TokenResponseSchema)
    @blp.login_required
    def post(self, item):
        """Add a new token"""
        token = Token(**item)
        db = current_app.session
        db.add(token)
        db.commit()
        return token


@blp.route('/<uuid:token_id>')
class TokensById(MethodView):
    @blp.etag
    @blp.query('token', TokenSchema)
    @blp.response(200, TokenResponseSchema)
    def get(self, token):
        """Get a token by ID"""
        return token

    @blp.etag
    @blp.query('token', TokenSchema)
    @blp.arguments(TokenSchema)
    @blp.response(200, TokenResponseSchema)
    @blp.login_required
    def put(self, new_token, token):
        """Replace a token identified by ID"""
        TokenSchema().put(token, Token(**new_token))
        db = current_app.session
        db.add(token)
        db.commit()
        return token

    @blp.etag
    @blp.query('token', TokenSchema)
    @blp.arguments(TokenUpdateSchema)
    @blp.response(200, TokenResponseSchema)
    @blp.login_required
    def patch(self, new_token, token):
        """Update a token identified by ID"""
        TokenSchema().patch(token, Token(**new_token))
        db = current_app.session
        db.add(token)
        db.commit()
        return token

    @blp.etag
    @blp.query('token', TokenSchema)
    @blp.response(204)
    @blp.login_required
    def delete(self, token):
        """Delete a token identified by ID"""
        db = current_app.session
        db.delete(token)
        db.commit()
