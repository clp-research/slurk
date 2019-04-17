from flask_wtf import FlaskForm
from wtforms.fields import StringField, SubmitField, IntegerField, SelectField, BooleanField
from wtforms import validators


class TokenGenerationForm(FlaskForm):
    source = StringField('Source')
    room = SelectField('Login room', validators=[validators.InputRequired()])
    task = SelectField('Task', validators=[validators.InputRequired()])
    count = IntegerField('Count', default=1)
    user_query = BooleanField('user_query', default=False)
    user_permissions_query = BooleanField('user_permissions_query', default=False)
    user_permissions_update = BooleanField('user_permissions_update', default=False)
    user_room_query = BooleanField('user_room_query', default=False)
    user_room_join = BooleanField('user_room_join', default=False)
    user_room_leave = BooleanField('user_room_leave', default=False)
    message_text = BooleanField('message_text', default=False)
    message_image = BooleanField('message_image', default=False)
    message_command = BooleanField('message_command', default=False)
    message_history = BooleanField('message_history', default=False)
    message_broadcast = BooleanField('message_broadcast', default=False)
    room_query = BooleanField('room_query', default=False)
    room_create = BooleanField('room_create', default=False)
    room_close = BooleanField('room_close', default=False)
    layout_query = BooleanField('layout_query', default=False)
    token_generate = BooleanField('token_generate', default=False)
    token_invalidate = BooleanField('token_invalidate', default=False)
    token_remove = BooleanField('token_remove', default=False)
    submit = SubmitField('Generate tokens')
