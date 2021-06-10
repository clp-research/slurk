from flask.views import MethodView
from marshmallow_sqlalchemy.schema import SQLAlchemySchema, auto_field
from sqlalchemy.sql.functions import mode

from app.extensions.api import Blueprint
from app import models

from . import CommonSchema


blp = Blueprint(models.Permissions.__tablename__, __name__)

API_DESC = (
    'Permit API calls',
    'Filter for API call permissions'
)
SEND_MESSAGE_DESC = (
    'Permit sending messages',
    'Filter for message sending permissions'
)
SEND_IMAGE_DESC = (
    'Permit sending images',
    'Filter for image sending permissions'
)
SEND_COMMAND_DESC = (
    'Permit sending commands',
    'Filter for command sending permissions'
)


# Base schema used for creating a `Log`.
class PermissionsSchema(CommonSchema, SQLAlchemySchema):
    class Meta:
        model = models.Permissions

    api = auto_field(missing=False, required=False, metadata={'description': API_DESC[0]})
    send_message = auto_field(missing=False, required=False, metadata={'description': SEND_MESSAGE_DESC[0]})
    send_image = auto_field(missing=False, required=False, metadata={'description': SEND_IMAGE_DESC[0]})
    send_command = auto_field(missing=False, required=False, metadata={'description': SEND_COMMAND_DESC[0]})


# Same as `PermissionsSchema` but Base schema but `required` set to false to prettify OpenAPI.
class PermissionsResponseSchema(PermissionsSchema):
    api = auto_field(required=False, metadata={'description': API_DESC[0]})
    send_message = auto_field(required=False, metadata={'description': SEND_MESSAGE_DESC[0]})
    send_image = auto_field(required=False, metadata={'description': SEND_IMAGE_DESC[0]})
    send_command = auto_field(required=False, metadata={'description': SEND_COMMAND_DESC[0]})


# Used for `PATCH`, which does not requires fields to be set
class PermissionsUpdateSchema(PermissionsSchema):
    api = auto_field(allow_none=True, required=False, metadata={'description': API_DESC[0]})
    send_message = auto_field(allow_none=True, required=False, metadata={'description': SEND_MESSAGE_DESC[0]})
    send_image = auto_field(allow_none=True, required=False, metadata={'description': SEND_IMAGE_DESC[0]})
    send_command = auto_field(allow_none=True, required=False, metadata={'description': SEND_COMMAND_DESC[0]})


# Same as `PermissionsUpdateSchema` but with other descriptions to prettify OpenAPI.
class PermissionsQuerySchema(PermissionsUpdateSchema):
    api = auto_field(allow_none=True, required=False, metadata={'description': API_DESC[1]})
    send_message = auto_field(allow_none=True, required=False, metadata={'description': SEND_MESSAGE_DESC[1]})
    send_image = auto_field(allow_none=True, required=False, metadata={'description': SEND_IMAGE_DESC[1]})
    send_command = auto_field(allow_none=True, required=False, metadata={'description': SEND_COMMAND_DESC[1]})


@blp.route('/')
class Permissions(MethodView):
    @blp.etag
    @blp.arguments(PermissionsQuerySchema, location='query')
    @blp.response(200, PermissionsResponseSchema(many=True))
    def get(self, args):
        """List permissions"""
        return PermissionsQuerySchema().list(args)

    @blp.etag
    @blp.arguments(PermissionsSchema, example=dict(api=True))
    @blp.response(201, PermissionsResponseSchema)
    @blp.login_required
    def post(self, item):
        """Add a new permissions"""
        return PermissionsSchema().post(item)


@blp.route('/<int:permissions_id>')
class PermissionsById(MethodView):
    @blp.etag
    @blp.query('permissions', PermissionsSchema)
    @blp.response(200, PermissionsResponseSchema)
    def get(self, *, permissions):
        """Get a permissions by ID"""
        return permissions

    @blp.etag
    @blp.query('permissions', PermissionsSchema)
    @blp.arguments(PermissionsSchema)
    @blp.response(200, PermissionsResponseSchema)
    @blp.login_required
    def put(self, new_permissions, *, permissions):
        """Replace a permissions identified by ID"""
        return PermissionsSchema().put(permissions, new_permissions)

    @blp.etag
    @blp.query('permissions', PermissionsSchema)
    @blp.arguments(PermissionsUpdateSchema)
    @blp.response(200, PermissionsResponseSchema)
    @blp.login_required
    def patch(self, new_permissions, *, permissions):
        """Update a permissions identified by ID"""
        return PermissionsUpdateSchema().patch(permissions, new_permissions)

    @blp.etag
    @blp.query('permissions', PermissionsSchema)
    @blp.response(204)
    @blp.login_required
    def delete(self, *, permissions):
        """Delete a permissions identified by ID"""
        PermissionsSchema().delete(permissions)
