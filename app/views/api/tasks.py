from flask.views import MethodView
import marshmallow as ma

from app.extensions.api import Blueprint
from app.models import Task, Layout
from app.views.api import CommonSchema, Id


blp = Blueprint(Task.__tablename__ + 's', __name__)


class TaskSchema(CommonSchema):
    class Meta:
        model = Task

    name = ma.fields.String(required=True, description='Name of the task', filter_description='Filter for a task name')
    num_users = ma.fields.Integer(required=True,
                                  description='Number of users needed for this task',
                                  filter_description='Filter for number of users needed for this task')
    layout_id = Id(table=Layout, required=True, description='Layout for this task',
                   filter_description='Filter for layout used in the tasks')


TaskCreationSchema = TaskSchema().creation_schema
TaskUpdateSchema = TaskSchema().update_schema
TaskResponseSchema = TaskSchema().response_schema
TaskQuerySchema = TaskSchema().query_schema


@blp.route('/')
class Tasks(MethodView):
    @blp.etag
    @blp.arguments(TaskQuerySchema, location='query')
    @blp.response(200, TaskResponseSchema(many=True))
    def get(self, args):
        """List tasks"""
        return TaskSchema().list(args)

    @blp.etag
    @blp.arguments(TaskCreationSchema)
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
    @blp.arguments(TaskCreationSchema)
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
