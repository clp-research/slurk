from flask_wtf import FlaskForm
from wtforms.fields import StringField, SubmitField, IntegerField, SelectField, BooleanField
from wtforms import validators


class TokenGenerationForm(FlaskForm):
    source = StringField('Source',
                         description="Optional field for tracking the origin of the token")
    room = SelectField('Login room',
                       validators=[validators.InputRequired()],
                       description="The room the user will join upon login")
    task = SelectField('Task',
                       validators=[validators.InputRequired()],
                       description="Task the token is assigned to")
    count = IntegerField('Count',
                         validators=[validators.InputRequired()],
                         default=1,
                         description="Number of tokens to generate")
    user_query = BooleanField('Query',
                              default=False,
                              description="Can query other users")
    user_log_query = BooleanField('Query logs',
                                  default=False,
                                  description="Can query the logs for an arbitrary user, the logs the user is in can "
                                              "always be queried")
    user_permissions_query = BooleanField('Query Permissions',
                                          default=False,
                                          description="Can query permissions of other user, the permissions for the "
                                                      "current can always be queried")
    user_permissions_update = BooleanField('Update Permissions',
                                           default=False,
                                           description="Can update permissions of a user")
    user_room_query = BooleanField('Query Room',
                                   default=False,
                                   description="Can query the rooms for an arbitrary user, the rooms the user is in "
                                               "can always be queried")
    user_room_join = BooleanField('Join Room',
                                  default=False,
                                  description="Can make users join a room")
    user_room_leave = BooleanField('Leave Room',
                                   default=False,
                                   description="Can make users leave a room")
    message_text = BooleanField('Text',
                                default=False,
                                description="Can send text messages")
    message_image = BooleanField('Image',
                                 default=False,
                                 description="Can send images")
    message_command = BooleanField('Command',
                                   default=False,
                                   description="Can submit commands")
    message_broadcast = BooleanField('Broadcast',
                                     default=False,
                                     description="Can broadcast messages")
    room_query = BooleanField('Query',
                              default=False,
                              description="Can query arbitrary rooms")
    room_log_query = BooleanField('Query Logs',
                                  default=False,
                                  description="Can query logs for an arbitrary rooms. Without this permission")
    room_create = BooleanField('Create',
                               default=False,
                               description="Can create a room")
    room_update = BooleanField('Update',
                               default=False,
                               description="Can update a rooms properties")
    room_close = BooleanField('Close',
                              default=False,
                              description="Can close a room")
    room_delete = BooleanField('Close',
                               default=False,
                               description="Can delete a room if there are no backrefs it it (tokens, users etc.)")
    layout_query = BooleanField('Query',
                                default=False,
                                description="Can query layouts of arbitrary rooms. The layout from the rooms the user "
                                            "is in can always be queried")
    task_create = BooleanField('Create',
                               default=False,
                               description="Can generate tasks. Needed to open the task form")
    task_query = BooleanField('Query',
                              default=False,
                              description="Can query tasks")
    token_generate = BooleanField('Generate',
                                  default=False,
                                  description="Can generate tokens. Needed to open this form")
    token_query = BooleanField('Query',
                               default=False,
                               description="Can query tokens. The token from the current user can always be queried")
    token_invalidate = BooleanField('Invalidate',
                                    default=False,
                                    description="Can invalidate tokens")
    token_remove = BooleanField('Remove',
                                default=False,
                                description="Can remove tokens")
    submit = SubmitField('Generate tokens',
                         description="Creates the token")


class TaskGenerationForm(FlaskForm):
    name = StringField('Name',
                       validators=[validators.InputRequired()],
                       description="The name of the task")
    num_users = IntegerField("Required Users",
                             validators=[validators.InputRequired()],
                             default=2,
                             description="Number of turkers required for this task")
    submit = SubmitField('Generate Task')
