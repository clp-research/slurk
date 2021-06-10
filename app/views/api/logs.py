from flask.views import MethodView
import marshmallow as ma
from marshmallow_sqlalchemy.schema import SQLAlchemySchema, auto_field

from app.extensions.api import Blueprint
from app.models import Log, User, Room

from . import CommonSchema, Id


blp = Blueprint(Log.__tablename__ + 's', __name__)

EVENT_DESC = (
    'The event associated with this log entry',
    'Filter by event'
)
USER_ID_DESC = (
    'Source user for this log entry',
    'Filter for user associated with this log entry'
)
ROOM_ID_DESC = (
    'Source room for this log entry',
    'Filter for room associated with this log entry'
)
RECEIVER_DESC = (
    'Receiver associated  with this log entry',
    'Filter for receiver associated with this log entry'
)
DATA_DESC = (
    'Data stored inside this log entry',
)


# Base schema used for creating a `Log`.
class LogSchema(CommonSchema, SQLAlchemySchema):
    class Meta:
        model = Log

    event = auto_field(metadata={'description': EVENT_DESC[0]})
    user_id = Id(table=User, allow_none=True, metadata={'description': USER_ID_DESC[0]})
    room_id = Id(table=Room, allow_none=True, metadata={'description': ROOM_ID_DESC[0]})
    receiver = Id(table=User, allow_none=True, metadata={'description': RECEIVER_DESC[0]})
    data = ma.fields.Dict(missing={}, metadata={'description': DATA_DESC[0]})


# Same as `LogSchema` but Base schema but `required` set to false to prettify OpenAPI.
class LogResponseSchema(LogSchema):
    event = auto_field(required=False, metadata={'description': EVENT_DESC[0]})
    data = ma.fields.Dict(metadata={'description': DATA_DESC[0]})


# Used for `PATCH`, which does not requires fields to be set
class LogUpdateSchema(LogSchema):
    event = auto_field(required=False, allow_none=True, metadata={'description': EVENT_DESC[0]})
    user_id = Id(table=User, allow_none=True, metadata={'description': USER_ID_DESC[0]})
    room_id = Id(table=Room, allow_none=True, metadata={'description': ROOM_ID_DESC[0]})
    receiver = Id(table=User, allow_none=True, metadata={'description': RECEIVER_DESC[0]})
    data = ma.fields.Dict(required=False, allow_none=True, metadata={'description': DATA_DESC[0]})


# Same as `LogUpdateSchema` but with other descriptions to prettify OpenAPI.
class LogQuerySchema(LogUpdateSchema):
    event = auto_field(required=False, allow_none=True, metadata={'description': EVENT_DESC[1]})
    user_id = Id(table=User, allow_none=True, metadata={'description': USER_ID_DESC[1]})
    room_id = Id(table=Room, allow_none=True, metadata={'description': ROOM_ID_DESC[1]})
    receiver = Id(table=User, allow_none=True, metadata={'description': RECEIVER_DESC[1]})
    data = auto_field(dump_only=True)


@blp.route('/')
class Logs(MethodView):
    @blp.etag
    @blp.arguments(LogQuerySchema, location='query')
    @blp.response(200, LogResponseSchema(many=True))
    @blp.login_required
    def get(self, args):
        """List logs"""
        return LogQuerySchema().list(args)

    @blp.etag
    @blp.arguments(LogSchema)
    @blp.response(201, LogResponseSchema)
    @blp.login_required
    def post(self, item):
        """Add a new log"""
        return LogSchema().post(item)


@blp.route('/<int:log_id>')
class LogById(MethodView):
    @blp.etag
    @blp.query('log', LogSchema)
    @blp.response(200, LogResponseSchema)
    @blp.login_required
    def get(self, *, log):
        """Get a log by ID"""
        return log

    @blp.etag
    @blp.query('log', LogSchema)
    @blp.arguments(LogSchema)
    @blp.response(200, LogResponseSchema)
    @blp.login_required
    def put(self, new_log, *, log):
        """Replace a log identified by ID"""
        return LogSchema().put(log, new_log)

    @blp.etag
    @blp.query('log', LogSchema)
    @blp.arguments(LogUpdateSchema)
    @blp.response(200, LogResponseSchema)
    @blp.login_required
    def patch(self, new_log, *, log):
        """Update a log identified by ID"""
        return LogUpdateSchema().patch(log, new_log)

    @blp.etag
    @blp.query('log', LogSchema)
    @blp.response(204)
    @blp.login_required
    def delete(self, *, log):
        """Delete a log identified by ID"""
        LogSchema().delete(log)
