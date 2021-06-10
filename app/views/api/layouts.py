from flask.views import MethodView
from marshmallow import fields
from marshmallow_sqlalchemy.schema import SQLAlchemySchema, auto_field
import marshmallow as ma

from app.extensions.api import Blueprint
from app.models import Layout

from . import CommonSchema


blp = Blueprint(Layout.__tablename__ + 's', __name__)


TITLE_DESC = (
    'Title of the layout',
    'Filter for a layout title'
)
SUBTITLE_DESC = (
    'Subtitle of the layout',
    'Filter for a layout subtitle'
)
HTML_DESC = (
    'HTML used in the layout',
)
CSS_DESC = (
    'Stylesheet used in the layout',
)
SCRIPTS_DESC = (
    'Scripts to be injected in the layout. Every field is either a string or a list of strings',
)
SCRIPT_DESC = (
    'Script injected in the layout',
)
SHOW_USERS_DESC = (
    'Show a user list in the layout',
    'Filter for a user list being shown'
)
SHOW_LATENCY_DESC = (
    'Show the current latency in the layout',
    'Filter for latency being shown'
)
READ_ONLY_DESC = (
    'Make the current room read-only',
    'Filter for the layout being read-only'
)

EXAMPLE = dict(
    title='Test Room',
    subtitle='Room for testing purposes',
    scripts={
        'incoming-text': 'display-text',
        'incoming-image': 'display-image',
        'submit-message': 'send-message',
        'print-history': 'plain-history',
    }
)


# Base schema, not used by marshmallow
class LayoutSchema(CommonSchema, SQLAlchemySchema):
    class Meta:
        model = Layout

    title = auto_field(metadata={'description': TITLE_DESC[0]}, allow_none=False)
    subtitle = auto_field(metadata={'description': SUBTITLE_DESC[0]})
    show_users = auto_field(missing=True, required=False, metadata={'description': SHOW_USERS_DESC[0]})
    show_latency = auto_field(missing=True, required=False, metadata={'description': SHOW_LATENCY_DESC[0]})
    read_only = auto_field(missing=False, required=False, metadata={'description': READ_ONLY_DESC[0]})

    def patch(self, old, new):
        # `scripts` is not stored in the database directly
        if 'scripts' in new:
            new['script'] = Layout.from_json_data(new).script
            del new['scripts']
        return super().patch(old, new)


script_dict = ma.Schema.from_dict({
    'incoming-text': ma.fields.Field(allow_none=True, metadata={'description': 'Called when a text message is received'}),
    'incoming-image': ma.fields.Field(allow_none=True, metadata={'description': 'Called when an image is received'}),
    'submit-message': ma.fields.Field(allow_none=True, metadata={'description': 'Called when a message is sent'}),
    'print-history': ma.fields.Field(allow_none=True, metadata={'description': 'Used for printing the chat history'}),
    'document-ready': ma.fields.Field(allow_none=True, metadata={'description': 'Called when site is fully loaded'}),
    'typing-users': ma.fields.Field(allow_none=True, metadata={'description': 'Called when state of currently typing users is changed'}),
    'plain': ma.fields.Field(allow_none=True, metadata={'description': 'Injected as a script file into the site'}),
}, name="Scripts")


# Used for `POST` and `GET`
class LayoutCreationSchema(LayoutSchema):
    html = ma.fields.Dict(allow_none=True, metadata={'description': HTML_DESC[0]})
    css = ma.fields.Dict(allow_none=True, metadata={'description': CSS_DESC[0]})
    scripts = ma.fields.Nested(script_dict, name='Scripts', allow_none=True, metadata={'description': SCRIPTS_DESC[0]})


# Used in responses. Differs from `LayoutCreationSchema` as `script` is generated from `scripts`, which is not stored
# in the database directly
class LayoutResponseSchema(LayoutSchema):
    title = auto_field(required=False, metadata={'description': TITLE_DESC[0]})
    html = auto_field(allow_none=True, metadata={'description': HTML_DESC[0]})
    css = auto_field(allow_none=True, metadata={'description': CSS_DESC[0]})
    script = auto_field(metadata={'description': SCRIPT_DESC[0]})
    show_users = auto_field(required=False, metadata={'description': SHOW_USERS_DESC[0]})
    show_latency = auto_field(required=False, metadata={'description': SHOW_LATENCY_DESC[0]})
    read_only = auto_field(required=False, metadata={'description': READ_ONLY_DESC[0]})


# Used for `PATCH`, `PATCH` does not require fields to be set
class LayoutUpdateSchema(LayoutCreationSchema):
    title = auto_field(allow_none=True, required=False, metadata={'description': TITLE_DESC[0]})
    html = ma.fields.Dict(allow_none=True, metadata={'description': HTML_DESC[0]})
    css = ma.fields.Dict(allow_none=True, metadata={'description': CSS_DESC[0]})
    show_users = auto_field(allow_none=True, required=False, metadata={'description': SHOW_USERS_DESC[0]})
    show_latency = auto_field(allow_none=True, required=False, metadata={'description': SHOW_LATENCY_DESC[0]})
    read_only = auto_field(allow_none=True, required=False, metadata={'description': READ_ONLY_DESC[0]})


# Used for querying in `GET`, so other descriptions are used
class LayoutQuerySchema(LayoutSchema):
    title = auto_field(allow_none=True, required=False, metadata={'description': TITLE_DESC[1]})
    subtitle = auto_field(metadata={'description': SUBTITLE_DESC[1]})
    show_users = auto_field(allow_none=True, required=False, metadata={'description': SHOW_USERS_DESC[1]})
    show_latency = auto_field(allow_none=True, required=False, metadata={'description': SHOW_LATENCY_DESC[1]})
    read_only = auto_field(allow_none=True, required=False, metadata={'description': READ_ONLY_DESC[1]})


@blp.route('/')
class Layouts(MethodView):
    @blp.etag
    @blp.arguments(LayoutQuerySchema, location='query')
    @blp.response(200, LayoutResponseSchema(many=True))
    def get(self, args):
        """List layouts"""
        return LayoutQuerySchema().list(args)

    @blp.etag
    @blp.arguments(LayoutCreationSchema, example=EXAMPLE)
    @blp.response(201, LayoutResponseSchema)
    @blp.login_required
    def post(self, item):
        """Add a new layout"""
        return LayoutCreationSchema().post(Layout.from_json_data(item))


@blp.route('/<int:layout_id>')
class LayoutById(MethodView):
    @blp.etag
    @blp.query('layout', LayoutResponseSchema)
    @blp.response(200, LayoutResponseSchema)
    def get(self, *, layout):
        """Get a layout by ID"""
        return layout

    @blp.etag
    @blp.query('layout', LayoutResponseSchema)
    @blp.arguments(LayoutCreationSchema)
    @blp.response(200, LayoutResponseSchema)
    @blp.login_required
    def put(self, new_layout, *, layout):
        """Replace a layout identified by ID"""
        return LayoutCreationSchema().put(layout, Layout.from_json_data(new_layout))

    @blp.etag
    @blp.query('layout', LayoutResponseSchema)
    @blp.arguments(LayoutUpdateSchema)
    @blp.response(200, LayoutResponseSchema)
    @blp.login_required
    def patch(self, new_layout, *, layout):
        """Update a layout identified by ID"""
        return LayoutResponseSchema().patch(layout, new_layout)

    @blp.etag
    @blp.query('layout', LayoutResponseSchema)
    @blp.response(204)
    @blp.login_required
    def delete(self, *, layout):
        """Delete a layout identified by ID"""
        LayoutResponseSchema().delete(layout)
