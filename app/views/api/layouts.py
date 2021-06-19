from flask.views import MethodView
from flask_smorest.error_handler import ErrorSchema
import marshmallow as ma

from app.extensions.api import Blueprint
from app.models import Layout
from app.views.api import CommonSchema


blp = Blueprint(Layout.__tablename__ + 's', __name__)


script_dict = ma.Schema.from_dict({
    'incoming-text': ma.fields.String(missing=None, description='Called when a text message is received'),
    'incoming-image': ma.fields.String(missing=None, description='Called when an image is received'),
    'submit-message': ma.fields.String(missing=None, description='Called when a message is sent'),
    'print-history': ma.fields.String(missing=None, description='Used for printing the chat history'),
    'typing-users': ma.fields.String(missing=None, description='Called when state of currently typing users is changed'),
    'document-ready': ma.fields.List(ma.fields.String, missing=None, description='Called when site is fully loaded'),
    'plain': ma.fields.List(ma.fields.String, missing=None, description='Injected as a script file into the site'),
}, name='Scripts')


class LayoutSchema(CommonSchema):
    class Meta:
        model = Layout

    title = ma.fields.String(
        required=True,
        description='Title of the layout',
        filter_description='Filter for a layout title')
    subtitle = ma.fields.String(
        missing=None,
        description='Subtitle of the layout',
        filter_description='Filter for a layout subtitle')
    html_obj = ma.fields.List(
        ma.fields.Dict,
        data_key='html',
        load_only=True,
        missing=[],
        description='HTML used in the layout')
    css_obj = ma.fields.Dict(
        data_key='css',
        load_only=True,
        missing={},
        description='Stylesheet used in the layout')
    scripts = ma.fields.Nested(
        script_dict,
        load_only=True,
        missing={},
        description='Scripts to be injected in the layout')
    html = ma.fields.String(
        dump_only=True,
        description=html_obj.metadata['description'])
    css = ma.fields.String(
        dump_only=True,
        description=css_obj.metadata['description'])
    script = ma.fields.String(
        dump_only=True,
        description='Script injected in the layout')
    show_users = ma.fields.Boolean(
        missing=True,
        description='Show a user list in the layout',
        filter_description='Filter for a user list being shown')
    show_latency = ma.fields.Boolean(
        missing=True,
        description='Show the current latency in the layout',
        filter_description='Filter for latency being shown')
    read_only = ma.fields.Boolean(
        missing=False,
        description='Make the room read-only',
        filter_description='Filter for the layout being read-only')
    start_with_audio = ma.fields.Boolean(
        missing=True,
        description='Start audio on joining the room if available',
        filter_description='Filter for starting audio on joining')
    start_with_video = ma.fields.Boolean(
        missing=True,
        description='Start video on joining the room if available',
        filter_description='Filter for starting video on joining')
    video_resolution = ma.fields.String(
        missing="640x480",
        description='Video resolution if available',
        filter_description='Filter for video resolution')
    video_framerate = ma.fields.Integer(
        missing=30,
        description='Framerate for video if available',
        filter_description='Filter for video framerate')

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


@blp.route('/')
class Layouts(MethodView):
    @blp.etag
    @blp.arguments(LayoutSchema.Filter, location='query')
    @blp.response(200, LayoutSchema.Response(many=True))
    def get(self, args):
        """List layouts"""
        return LayoutSchema().list(args)

    @blp.etag
    @blp.arguments(LayoutSchema.Creation, location='json', example=EXAMPLE)
    @blp.response(201, LayoutSchema.Response)
    @blp.login_required
    def post(self, item):
        """Add a new layout"""
        return LayoutSchema().post(Layout.from_json_data(item))


@blp.route('/<int:layout_id>')
class LayoutById(MethodView):
    @blp.etag
    @blp.query('layout', LayoutSchema)
    @blp.response(200, LayoutSchema.Response)
    def get(self, *, layout):
        """Get a layout by ID"""
        return layout

    @blp.etag
    @blp.query('layout', LayoutSchema)
    @blp.arguments(LayoutSchema.Creation, location='json')
    @blp.response(200, LayoutSchema.Response)
    @blp.login_required
    def put(self, new_layout, *, layout):
        """Replace a layout identified by ID"""
        return LayoutSchema().put(layout, Layout.from_json_data(new_layout))

    @blp.etag
    @blp.query('layout', LayoutSchema)
    @blp.arguments(LayoutSchema.Update, location='json')
    @blp.response(200, LayoutSchema.Response)
    @blp.login_required
    def patch(self, new_layout, *, layout):
        """Update a layout identified by ID"""
        return LayoutSchema().patch(layout, new_layout)

    @blp.etag
    @blp.query('layout', LayoutSchema)
    @blp.response(204)
    @blp.alt_response(422, ErrorSchema)
    @blp.login_required
    def delete(self, *, layout):
        """Delete a layout identified by ID"""
        LayoutSchema().delete(layout)
