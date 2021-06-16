from flask.views import MethodView
import marshmallow as ma

from app.extensions.api import Blueprint
from app.models import Permissions
from app.views.api import CommonSchema


blp = Blueprint(Permissions.__tablename__, __name__)


class PermissionsSchema(CommonSchema):
    class Meta:
        model = Permissions

    api = ma.fields.Boolean(
        missing=False,
        description='Permit API calls',
        filter_description='Filter for API call permissions')
    send_message = ma.fields.Boolean(
        missing=False,
        description='Permit sending messages',
        filter_description='Filter for message sending permissions')
    send_image = ma.fields.Boolean(
        missing=False,
        description='Permit sending images',
        filter_description='Filter for image sending permissions')
    send_command = ma.fields.Boolean(
        missing=False,
        description='Permit sending commands',
        filter_description='Filter for command sending permissions')


@blp.route('/')
class Permissions(MethodView):
    @blp.etag
    @blp.arguments(PermissionsSchema.Filter, location='query')
    @blp.response(200, PermissionsSchema.Response(many=True))
    def get(self, args):
        """List permissions"""
        return PermissionsSchema().list(args)

    @blp.etag
    @blp.arguments(PermissionsSchema.Creation, example=dict(api=True))
    @blp.response(201, PermissionsSchema.Response)
    @blp.login_required
    def post(self, item):
        """Add a new permissions"""
        return PermissionsSchema().post(item)


@blp.route('/<int:permissions_id>')
class PermissionsById(MethodView):
    @blp.etag
    @blp.query('permissions', PermissionsSchema)
    @blp.response(200, PermissionsSchema.Response)
    def get(self, *, permissions):
        """Get a permissions by ID"""
        return permissions

    @blp.etag
    @blp.query('permissions', PermissionsSchema)
    @blp.arguments(PermissionsSchema.Creation)
    @blp.response(200, PermissionsSchema.Response)
    @blp.login_required
    def put(self, new_permissions, *, permissions):
        """Replace a permissions identified by ID"""
        return PermissionsSchema().put(permissions, new_permissions)

    @blp.etag
    @blp.query('permissions', PermissionsSchema)
    @blp.arguments(PermissionsSchema.Update)
    @blp.response(200, PermissionsSchema.Response)
    @blp.login_required
    def patch(self, new_permissions, *, permissions):
        """Update a permissions identified by ID"""
        return PermissionsSchema().patch(permissions, new_permissions)

    @blp.etag
    @blp.query('permissions', PermissionsSchema)
    @blp.response(204)
    @blp.login_required
    def delete(self, *, permissions):
        """Delete a permissions identified by ID"""
        PermissionsSchema().delete(permissions)
