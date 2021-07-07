from flask.views import MethodView
import marshmallow as ma

from app.extensions.api import Blueprint
from app.models import Log, User, Room
from app.views.api import CommonSchema, Id


blp = Blueprint(Log.__tablename__, __name__)


class LogSchema(CommonSchema):
    class Meta:
        model = Log

    event = ma.fields.String(
        required=True,
        description='The event associated with this log entry',
        filter_description='Filter by event')
    user_id = Id(
        User,
        missing=None,
        description='Source user for this log entry',
        filter_description='Filter for user associated with this log entry')
    room_id = Id(
        Room,
        missing=None,
        description='Source room for this log entry',
        filter_description='Filter for room associated with this log entry')
    receiver_id = Id(
        User,
        missing=None,
        description='Receiver associated  with this log entry',
        filter_description='Filter for receiver associated with this log entry')
    data = ma.fields.Dict(missing={}, description='Data stored inside this log entry')


@blp.route('/')
class Logs(MethodView):
    @blp.etag
    @blp.arguments(LogSchema.Filter, location='query')
    @blp.response(200, LogSchema.Response(many=True))
    @blp.login_required
    def get(self, args):
        """List logs"""
        return LogSchema().list(args)

    @blp.etag
    @blp.arguments(LogSchema.Creation)
    @blp.response(201, LogSchema.Response)
    @blp.login_required
    def post(self, item):
        """Add a new log"""
        return LogSchema().post(item)


@blp.route('/<int:log_id>')
class LogById(MethodView):
    @blp.etag
    @blp.query('log', LogSchema)
    @blp.response(200, LogSchema.Response)
    @blp.login_required
    def get(self, *, log):
        """Get a log by ID"""
        return log

    @blp.etag
    @blp.query('log', LogSchema)
    @blp.arguments(LogSchema.Creation)
    @blp.response(200, LogSchema.Response)
    @blp.login_required
    def put(self, new_log, *, log):
        """Replace a log identified by ID"""
        return LogSchema().put(log, new_log)

    @blp.etag
    @blp.query('log', LogSchema)
    @blp.arguments(LogSchema.Update)
    @blp.response(200, LogSchema.Response)
    @blp.login_required
    def patch(self, new_log, *, log):
        """Update a log identified by ID"""
        return LogSchema().patch(log, new_log)

    @blp.etag
    @blp.query('log', LogSchema)
    @blp.response(204)
    @blp.login_required
    def delete(self, *, log):
        """Delete a log identified by ID"""
        LogSchema().delete(log)
