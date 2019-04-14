from flask_wtf import FlaskForm
from wtforms.fields import StringField, SubmitField, IntegerField, SelectField, BooleanField
from wtforms import validators


class TokenGenerationForm(FlaskForm):
    source = StringField('Source')
    room = SelectField('Login room', validators=[validators.InputRequired()])
    task = SelectField('Task', validators=[validators.InputRequired()])
    count = IntegerField('Count', default=1)
    key = StringField('Key', [validators.DataRequired()])
    query_user = BooleanField('query_user', default=False)
    query_room = BooleanField('query_room', default=False)
    query_permissions = BooleanField('query_permissions', default=False)
    message_send = BooleanField('message_send', default=False)
    message_history = BooleanField('message_history', default=False)
    message_broadcast = BooleanField('message_history', default=False)
    submit = SubmitField('Generate tokens')
