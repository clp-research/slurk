from flask_wtf import FlaskForm
from wtforms.fields import StringField, SubmitField, IntegerField, SelectField, BooleanField
from wtforms import validators


class TokenGenerationForm(FlaskForm):
    source = StringField('Source')
    room = SelectField('Login room', validators=[validators.InputRequired()])
    task = SelectField('Task', validators=[validators.InputRequired()])
    count = IntegerField('Count', default=1)
    query_user = BooleanField('query_user', default=False)
    query_room = BooleanField('query_room', default=False)
    query_permissions = BooleanField('query_permissions', default=False)
    query_layout = BooleanField('query_layout', default=False)
    message_text = BooleanField('message_text', default=False)
    message_image = BooleanField('message_image', default=False)
    message_command = BooleanField('message_command', default=False)
    message_history = BooleanField('message_history', default=False)
    message_broadcast = BooleanField('message_broadcast', default=False)
    token_generate = BooleanField('token_generate', default=False)
    token_invalidate = BooleanField('token_invalidate', default=False)
    submit = SubmitField('Generate tokens')
