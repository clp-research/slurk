from flask.views import MethodView
import marshmallow as ma

from app.extensions.api import Blueprint
from app.models import Layout
from app.views.api import CommonSchema


blp = Blueprint(Layout.__tablename__ + 's', __name__)


script_dict = ma.Schema.from_dict({
    'incoming-text': ma.fields.List(ma.fields.String, missing=None, metadata={'description': 'Called when a text message is received'}),
    'incoming-image': ma.fields.List(ma.fields.String, missing=None, metadata={'description': 'Called when an image is received'}),
    'submit-message': ma.fields.List(ma.fields.String, missing=None, metadata={'description': 'Called when a message is sent'}),
    'print-history': ma.fields.List(ma.fields.String, missing=None, metadata={'description': 'Used for printing the chat history'}),
    'document-ready': ma.fields.List(ma.fields.String, missing=None, metadata={'description': 'Called when site is fully loaded'}),
    'typing-users': ma.fields.List(ma.fields.String, missing=None, metadata={'description': 'Called when state of currently typing users is changed'}),
    'plain': ma.fields.List(ma.fields.String, missing=None, metadata={'description': 'Injected as a script file into the site'}),
}, name="Scripts")


class LayoutSchema(CommonSchema):
    class Meta:
        model = Layout

    title = ma.fields.String(required=True, description='Title of the layout',
                             filter_description='Filter for a layout title')
    subtitle = ma.fields.String(missing=None, description='Subtitle of the layout',
                                filter_description='Filter for a layout subtitle')
    html_obj = ma.fields.List(ma.fields.Dict, load_only=True, missing={}, data_key='html', description='HTML used in the layout')
    css_obj = ma.fields.Dict(load_only=True, missing={}, data_key='css', description='Stylesheet used in the layout')
    scripts = ma.fields.Nested(script_dict, load_only=True, missing={},
                               description='Scripts to be injected in the layout')
    html = ma.fields.String(dump_only=True, data_key='html', description=html_obj.metadata['description'])
    css = ma.fields.String(dump_only=True, data_key='css', description=css_obj.metadata['description'])
    script = ma.fields.String(dump_only=True, description='Script injected in the layout')
    show_users = ma.fields.Boolean(missing=True,
                                   description='Show a user list in the layout',
                                   filter_description='Filter for a user list being shown')
    show_latency = ma.fields.Boolean(missing=True,
                                     description='Show the current latency in the layout',
                                     filter_description='Filter for latency being shown')
    read_only = ma.fields.Boolean(missing=False, description='Make the room read-only',
                                  filter_description='Filter for the layout being read-only')

    def patch(self, old, new):
        layout = Layout.from_json_data(new)
        if 'html_obj' in new:
            new['html'] = layout.html
            del new['html_obj']
        if 'css_obj' in new:
            new['css'] = layout.css
            del new['css_obj']
        if 'scripts' in new:
            new['script'] = layout.script
            del new['scripts']
        return super().patch(old, new)


LayoutCreationSchema = LayoutSchema().creation_schema
LayoutUpdateSchema = LayoutSchema().update_schema
LayoutResponseSchema = LayoutSchema().response_schema
LayoutQuerySchema = LayoutSchema().query_schema


EXAMPLE = dict(
    title='Test Room',
    subtitle='Room for testing purposes',
    scripts={
        'incoming-text': ['display-text'],
        'incoming-image': ['display-image'],
        'submit-message': ['send-message'],
        'print-history': ['plain-history'],
    }
)


@blp.route('/')
class Layouts(MethodView):
    @blp.etag
    @blp.arguments(LayoutQuerySchema, location='query')
    @blp.response(200, LayoutResponseSchema(many=True))
    def get(self, args):
        """List layouts"""
        return LayoutSchema().list(args)

    @blp.etag
    @blp.arguments(LayoutCreationSchema, location='json', example=EXAMPLE)
    @blp.response(201, LayoutResponseSchema)
    @blp.login_required
    def post(self, item):
        """Add a new layout"""
        return LayoutSchema().post(Layout.from_json_data(item))


@blp.route('/<int:layout_id>')
class LayoutById(MethodView):
    @blp.etag
    @blp.query('layout', LayoutSchema)
    @blp.response(200, LayoutResponseSchema)
    def get(self, *, layout):
        """Get a layout by ID"""
        return layout

    @blp.etag
    @blp.query('layout', LayoutSchema)
    @blp.arguments(LayoutCreationSchema, location='json')
    @blp.response(200, LayoutResponseSchema)
    @blp.login_required
    def put(self, new_layout, *, layout):
        """Replace a layout identified by ID"""
        return LayoutSchema().put(layout, Layout.from_json_data(new_layout))

    @blp.etag
    @blp.query('layout', LayoutSchema)
    @blp.arguments(LayoutUpdateSchema, location='json')
    @blp.response(200, LayoutResponseSchema)
    @blp.login_required
    def patch(self, new_layout, *, layout):
        """Update a layout identified by ID"""
        return LayoutSchema().patch(layout, new_layout)

    @blp.etag
    @blp.query('layout', LayoutSchema)
    @blp.response(204)
    @blp.login_required
    def delete(self, *, layout):
        """Delete a layout identified by ID"""
        LayoutSchema().delete(layout)
