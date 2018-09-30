from flask_wtf import FlaskForm
from wtforms.fields import StringField, SubmitField, BooleanField, IntegerField, SelectField
from wtforms.validators import InputRequired


class LoginForm(FlaskForm):
    name = StringField('Name', validators=[InputRequired()])
    token = StringField('Token', validators=[InputRequired()])
    submit = SubmitField('Enter Chatroom')


class TokenGenerationForm(FlaskForm):
    source = StringField('Source')
    room = SelectField('Login room', validators=[InputRequired()])
    task = SelectField('Task', validators=[InputRequired()])
    count = IntegerField('Count', default=1)
    submit = SubmitField('Generate tokens')
