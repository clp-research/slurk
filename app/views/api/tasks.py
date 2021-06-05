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

# Only two schemas are needed but four are used to prettify OpenAPI Documentation


class TaskSchema(CommonSchema, SQLAlchemySchema):
    class Meta:
        model = Task

    name = auto_field(metadata={'description': NAME_DESC[0]})
    num_users = auto_field(metadata={'description': NUM_USERS_DESC[0]})
    layout_id = Id(table=Token, required=True, metadata={'description': LAYOUT_ID_DESC[0]})


class TaskResponseSchema(TaskSchema):
    name = auto_field(required=False, metadata={'description': NAME_DESC[0]})
    num_users = auto_field(required=False, metadata={'description': NUM_USERS_DESC[0]})
    layout_id = Id(table=Token, metadata={'description': LAYOUT_ID_DESC[0]})


class TaskUpdateSchema(TaskResponseSchema):
    name = auto_field(required=False, allow_none=True, metadata={'description': NAME_DESC[0]})
    num_users = auto_field(required=False, allow_none=True, metadata={'description': NUM_USERS_DESC[0]})
    layout_id = Id(table=Token, allow_none=True, metadata={'description': LAYOUT_ID_DESC[0]})


class TaskQuerySchema(TaskSchema):
    name = auto_field(required=False, allow_none=True, metadata={'description': NAME_DESC[1]})
    num_users = auto_field(required=False, allow_none=True, metadata={'description': NUM_USERS_DESC[1]})
    layout_id = Id(table=Token, allow_none=True, metadata={'description': LAYOUT_ID_DESC[1]})


@blp.route('/')
class Tasks(MethodView):
    @blp.etag
    @blp.arguments(TaskQuerySchema, location='query')
    @blp.response(200, TaskResponseSchema(many=True))
    @blp.paginate()
    def get(self, args, pagination_parameters):
        """List tasks"""
        db = current_app.session
        query = db.query(Task) \
            .filter_by(**args) \
            .order_by(Task.date_created.desc())
        pagination_parameters.item_count = query.count()
        return query \
            .limit(pagination_parameters.page_size) \
            .offset(pagination_parameters.first_item) \
            .all()

    @blp.etag
    @blp.arguments(TaskSchema)
    @blp.response(201, TaskResponseSchema)
    @blp.login_required
    def post(self, item):
        """Add a new task"""
        task = Task(**item)
        db = current_app.session
        db.add(task)
        db.commit()
        return task


@blp.route('/<int:task_id>')
class TaskById(MethodView):
    @blp.etag
    @blp.query('task', TaskSchema)
    @blp.response(200, TaskResponseSchema)
    def get(self, task):
        """Get a task by ID"""
        return task

    @blp.etag
    @blp.query('task', TaskSchema)
    @blp.arguments(TaskSchema)
    @blp.response(200, TaskResponseSchema)
    @blp.login_required
    def put(self, new_task, task):
        """Replace a task identified by ID"""
        task = TaskSchema().put(task, Task(**new_task))
        db = current_app.session
        db.add(task)
        db.commit()
        return task

    @blp.etag
    @blp.query('task', TaskSchema)
    @blp.arguments(TaskUpdateSchema)
    @blp.response(200, TaskResponseSchema)
    @blp.login_required
    def patch(self, new_task, task):
        """Update a task identified by ID"""
        task = TaskSchema().patch(task, Task(**new_task))
        db = current_app.session
        db.add(task)
        db.commit()
        return task

    @blp.etag
    @blp.query('task', TaskSchema)
    @blp.response(204)
    @blp.login_required
    def delete(self, task):
        """Delete a task identified by ID"""
        db = current_app.session
        db.delete(task)
        db.commit()
