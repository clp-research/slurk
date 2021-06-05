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


# Only two schemas are needed but four are used to prettify OpenAPI Documentation
class UserSchema(CommonSchema, SQLAlchemySchema):
    class Meta:
        model = User

    name = auto_field(metadata={'description': NAME_DESC[0]})
    token_id = TokenId(required=True, load_only=True, metadata={'description': TOKEN_ID_DESC[0]})
    session_id = auto_field(dump_only=True, metadata={'description': SESSION_ID_DESC[0]})


class UserResponseSchema(UserSchema):
    name = auto_field(required=False, metadata={'description': NAME_DESC[0]})


class UserUpdateSchema(UserSchema):
    name = auto_field(allow_none=True, required=False, metadata={'description': NAME_DESC[0]})
    token_id = TokenId(allow_none=True, metadata={'description': TOKEN_ID_DESC[0]})


class UserQuerySchema(UserSchema):
    name = auto_field(allow_none=True, required=False, metadata={'description': NAME_DESC[1]})
    token_id = TokenId(allow_none=True, metadata={'description': TOKEN_ID_DESC[1]})
    session_id = auto_field(metadata={'description': SESSION_ID_DESC[1]})


@blp.route('/')
class Users(MethodView):
    @blp.etag
    @blp.arguments(UserQuerySchema, location='query')
    @blp.response(200, UserResponseSchema(many=True))
    @blp.paginate()
    def get(self, args, pagination_parameters):
        """List users"""
        db = current_app.session
        query = db.query(User) \
            .filter_by(**args) \
            .order_by(User.date_created.desc())
        pagination_parameters.item_count = query.count()
        return query \
            .limit(pagination_parameters.page_size) \
            .offset(pagination_parameters.first_item) \
            .all()

    @blp.etag
    @blp.arguments(UserSchema)
    @blp.response(201, UserResponseSchema)
    @blp.login_required
    def post(self, item):
        """Add a new user"""
        user = User(**item)
        db = current_app.session
        db.add(user)
        db.commit()
        return user


@blp.route('/<int:user_id>')
class UserById(MethodView):
    @blp.etag
    @blp.query('user', UserSchema)
    @blp.response(200, UserResponseSchema)
    def get(self, user):
        """Get a user by ID"""
        return user

    @blp.etag
    @blp.query('user', UserSchema)
    @blp.arguments(UserSchema)
    @blp.response(200, UserResponseSchema)
    @blp.login_required
    def put(self, new_user, user):
        """Replace a user identified by ID"""
        user = UserSchema().put(user, User(**new_user))
        db = current_app.session
        db.add(user)
        db.commit()
        return user

    @blp.etag
    @blp.query('user', UserSchema)
    @blp.arguments(UserUpdateSchema)
    @blp.response(200, UserResponseSchema)
    @blp.login_required
    def patch(self, new_user, user):
        """Update a user identified by ID"""
        user = UserSchema().patch(user, User(**new_user))
        db = current_app.session
        db.add(user)
        db.commit()
        return user

    @blp.etag
    @blp.query('user', UserSchema)
    @blp.response(204)
    @blp.login_required
    def delete(self, user):
        """Delete a user identified by ID"""
        db = current_app.session
        db.delete(user)
        db.commit()
