from flask.views import MethodView
from flask_smorest.error_handler import ErrorSchema
import marshmallow as ma

from app.extensions.api import Blueprint
from app.models import Task, Layout
from app.views.api import CommonSchema, Id


blp = Blueprint(Task.__tablename__ + 's', __name__)


class TaskSchema(CommonSchema):
    class Meta:
        model = Task

    name = ma.fields.String(
        required=True,
        description='Name of the task',
        filter_description='Filter for a task name')
    num_users = ma.fields.Integer(
        validate=ma.validate.Range(min=0, max=2**63 - 1),
        required=True,
        description='Number of users needed for this task',
        filter_description='Filter for number of users needed for this task')
    layout_id = Id(
        Layout,
        required=True,
        description='Layout for this task',
        filter_description='Filter for layout used in the tasks')


@blp.route('/')
class Tasks(MethodView):
    @blp.etag
    @blp.arguments(TaskSchema.Filter, location='query')
    @blp.response(200, TaskSchema.Response(many=True))
    def get(self, args):
        """List tasks"""
        return TaskSchema().list(args)

    @blp.etag
    @blp.arguments(TaskSchema.Creation)
    @blp.response(201, TaskSchema.Response)
    @blp.login_required
    def post(self, item):
        """Add a new task"""
        return TaskSchema().post(item)


@blp.route('/<int:task_id>')
class TaskById(MethodView):
    @blp.etag
    @blp.query('task', TaskSchema)
    @blp.response(200, TaskSchema.Response)
    def get(self, *, task):
        """Get a task by ID"""
        return task

    @blp.etag
    @blp.query('task', TaskSchema)
    @blp.arguments(TaskSchema.Creation)
    @blp.response(200, TaskSchema.Response)
    @blp.login_required
    def put(self, new_task, *, task):
        """Replace a task identified by ID"""
        return TaskSchema().put(task, new_task)

    @blp.etag
    @blp.query('task', TaskSchema)
    @blp.arguments(TaskSchema.Update)
    @blp.response(200, TaskSchema.Response)
    @blp.login_required
    def patch(self, new_task, *, task):
        """Update a task identified by ID"""
        return TaskSchema().patch(task, new_task)

    @blp.etag
    @blp.query('task', TaskSchema)
    @blp.response(204)
    @blp.alt_response(422, ErrorSchema)
    @blp.login_required
    def delete(self, *, task):
        """Delete a task identified by ID"""
        TaskSchema().delete(task)
