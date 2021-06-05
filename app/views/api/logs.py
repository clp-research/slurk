from flask.views import MethodView
from flask.globals import current_app
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


# Only two schemas are needed but four are used to prettify OpenAPI Documentation
class LogSchema(CommonSchema, SQLAlchemySchema):
    class Meta:
        model = Log

    event = auto_field(metadata={'description': EVENT_DESC[0]})
    user_id = Id(table=User, allow_none=True, metadata={'description': USER_ID_DESC[0]})
    room_id = Id(table=Room, allow_none=True, metadata={'description': ROOM_ID_DESC[0]})
    receiver = Id(table=User, allow_none=True, metadata={'description': RECEIVER_DESC[0]})
    data = ma.fields.Dict(required=True, metadata={'description': DATA_DESC[0]})


class LogResponseSchema(LogSchema):
    event = auto_field(required=False, metadata={'description': EVENT_DESC[0]})
    data = ma.fields.Dict(metadata={'description': DATA_DESC[0]})


class LogUpdateSchema(LogResponseSchema):
    event = auto_field(required=False, allow_none=True, metadata={'description': EVENT_DESC[0]})
    user_id = Id(table=User, allow_none=True, metadata={'description': USER_ID_DESC[0]})
    room_id = Id(table=Room, allow_none=True, metadata={'description': ROOM_ID_DESC[0]})
    receiver = Id(table=User, allow_none=True, metadata={'description': RECEIVER_DESC[0]})
    data = ma.fields.Dict(required=False, allow_none=True, metadata={'description': DATA_DESC[0]})


class LogQuerySchema(LogSchema):
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
    @blp.paginate()
    def get(self, args, pagination_parameters):
        """List logs"""
        db = current_app.session
        query = db.query(Log) \
            .filter_by(**args) \
            .order_by(Log.date_created.desc())
        pagination_parameters.item_count = query.count()
        return query \
            .limit(pagination_parameters.page_size) \
            .offset(pagination_parameters.first_item) \
            .all()

    @blp.etag
    @blp.arguments(LogSchema)
    @blp.response(201, LogResponseSchema)
    @blp.login_required
    def post(self, item):
        """Add a new log"""
        log = Log(**item)
        db = current_app.session
        db.add(log)
        db.commit()
        return log


@blp.route('/<int:log_id>')
class LogById(MethodView):
    @blp.etag
    @blp.query('log', LogSchema)
    @blp.response(200, LogResponseSchema)
    def get(self, log):
        """Get a log by ID"""
        return log

    @blp.etag
    @blp.query('log', LogSchema)
    @blp.arguments(LogSchema)
    @blp.response(200, LogResponseSchema)
    @blp.login_required
    def put(self, new_log, log):
        """Replace a log identified by ID"""
        log = LogSchema().put(log, Log(**new_log))
        db = current_app.session
        db.add(log)
        db.commit()
        return log

    @blp.etag
    @blp.query('log', LogSchema)
    @blp.arguments(LogUpdateSchema)
    @blp.response(200, LogResponseSchema)
    @blp.login_required
    def patch(self, new_log, log):
        """Update a log identified by ID"""
        log = LogSchema().patch(log, Log(**new_log))
        db = current_app.session
        db.add(log)
        db.commit()
        return log

    @blp.etag
    @blp.query('log', LogSchema)
    @blp.response(204)
    @blp.login_required
    def delete(self, log):
        """Delete a log identified by ID"""
        db = current_app.session
        db.delete(log)
        db.commit()
