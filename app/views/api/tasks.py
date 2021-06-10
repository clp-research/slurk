from flask.views import MethodView
from flask.globals import current_app
from marshmallow_sqlalchemy.schema import SQLAlchemySchema, auto_field

from app.extensions.api import Blueprint
from app.models import Task, Token

from . import CommonSchema, Id


blp = Blueprint(Task.__tablename__ + 's', __name__)


NAME_DESC = (
    'Name of the task',
    'Filter for a task name'
)
NUM_USERS_DESC = (
    'Number of users needed for this task',
    'Filter for number of users needed for this task'
)
LAYOUT_ID_DESC = (
    'Layout for this task',
    'Filter for layout used in the tasks'
)


# Base schema used for creating a `Log`.
class TaskSchema(CommonSchema, SQLAlchemySchema):
    class Meta:
        model = Task

    name = auto_field(metadata={'description': NAME_DESC[0]})
    num_users = auto_field(metadata={'description': NUM_USERS_DESC[0]})
    layout_id = Id(table=Token, required=True, metadata={'description': LAYOUT_ID_DESC[0]})


# Same as `TaskSchema` but Base schema but `required` set to false to prettify OpenAPI.
class TaskResponseSchema(TaskSchema):
    name = auto_field(required=False, metadata={'description': NAME_DESC[0]})
    num_users = auto_field(required=False, metadata={'description': NUM_USERS_DESC[0]})
    layout_id = Id(table=Token, metadata={'description': LAYOUT_ID_DESC[0]})


# Used for `PATCH`, which does not requires fields to be set
class TaskUpdateSchema(TaskSchema):
    name = auto_field(required=False, allow_none=True, metadata={'description': NAME_DESC[0]})
    num_users = auto_field(required=False, allow_none=True, metadata={'description': NUM_USERS_DESC[0]})
    layout_id = Id(table=Token, allow_none=True, metadata={'description': LAYOUT_ID_DESC[0]})


# Same as `TaskUpdateSchema` but with other descriptions to prettify OpenAPI.
class TaskQuerySchema(TaskUpdateSchema):
    name = auto_field(required=False, allow_none=True, metadata={'description': NAME_DESC[1]})
    num_users = auto_field(required=False, allow_none=True, metadata={'description': NUM_USERS_DESC[1]})
    layout_id = Id(table=Token, allow_none=True, metadata={'description': LAYOUT_ID_DESC[1]})


@blp.route('/')
class Tasks(MethodView):
    @blp.etag
    @blp.arguments(TaskQuerySchema, location='query')
    @blp.response(200, TaskResponseSchema(many=True))
    def get(self, args):
        """List tasks"""
        return TaskQuerySchema().list(args)

    @blp.etag
    @blp.arguments(TaskSchema)
    @blp.response(201, TaskResponseSchema)
    @blp.login_required
    def post(self, item):
        """Add a new task"""
        return TaskSchema().post(item)


@blp.route('/<int:task_id>')
class TaskById(MethodView):
    @blp.etag
    @blp.query('task', TaskSchema)
    @blp.response(200, TaskResponseSchema)
    def get(self, *, task):
        """Get a task by ID"""
        return task

    @blp.etag
    @blp.query('task', TaskSchema)
    @blp.arguments(TaskSchema)
    @blp.response(200, TaskResponseSchema)
    @blp.login_required
    def put(self, new_task, *, task):
        """Replace a task identified by ID"""
        return TaskSchema().put(task, new_task)

    @blp.etag
    @blp.query('task', TaskSchema)
    @blp.arguments(TaskUpdateSchema)
    @blp.response(200, TaskResponseSchema)
    @blp.login_required
    def patch(self, new_task, *, task):
        """Update a task identified by ID"""
        return TaskUpdateSchema().patch(task, new_task)

    @blp.etag
    @blp.query('task', TaskSchema)
    @blp.response(204)
    @blp.login_required
    def delete(self, *, task):
        """Delete a task identified by ID"""
        TaskSchema().delete(task)
