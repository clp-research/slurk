from flask_wtf import FlaskForm
from wtforms.fields import StringField, SubmitField, BooleanField, IntegerField, SelectField, PasswordField
from wtforms import validators

from .. import config


class LoginForm(FlaskForm):
    name = StringField('Name', validators=[validators.InputRequired()])
    token = StringField('Token', validators=[validators.InputRequired()])
    submit = SubmitField('Enter Chatroom')


class AdminForm(FlaskForm):
    name = StringField('Name', validators=[validators.InputRequired()])
    label = StringField('Label', validators=[validators.InputRequired()])
    layout = StringField('Layout', validators=[validators.InputRequired()])
    readonly = BooleanField('Readonly')
    showusers = BooleanField('Show users', default=True)
    showlatency = BooleanField('Show latency', default=True)
    showinput = BooleanField('Show input', default=True)
    showhistory = BooleanField('Show History', default=True)
    showinteractionarea = BooleanField('Show interaction area', default=True)
    submit = SubmitField('Enter Chatroom')
    key = StringField('Key', [validators.DataRequired()])
    submit = SubmitField('Create Room')


class TokenGenerationForm(FlaskForm):
    source = StringField('Source')
    room = SelectField('Login room', validators=[validators.InputRequired()])
    task = SelectField('Task', validators=[validators.InputRequired()])
    count = IntegerField('Count', default=1)
    key = StringField('Key', [validators.DataRequired()])
    submit = SubmitField('Generate tokens')
