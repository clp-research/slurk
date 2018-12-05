from flask_wtf import FlaskForm
from wtforms.fields import StringField, SubmitField, BooleanField, IntegerField, SelectField, PasswordField
from wtforms import validators

from .. import config


class LoginForm(FlaskForm):
    name = StringField('Name', validators=[validators.InputRequired()])
    token = StringField('Token', validators=[validators.InputRequired()])
    submit = SubmitField('Enter Chatroom')


class TokenGenerationForm(FlaskForm):
    source = StringField('Source')
    room = SelectField('Login room', validators=[validators.InputRequired()])
    task = SelectField('Task', validators=[validators.InputRequired()])
    count = IntegerField('Count', default=1)
    key = StringField('Key', [validators.DataRequired()])
    submit = SubmitField('Generate tokens')
