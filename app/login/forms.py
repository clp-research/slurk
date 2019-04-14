from flask_wtf import FlaskForm
from wtforms.fields import StringField, SubmitField
from wtforms import validators


class LoginForm(FlaskForm):
    name = StringField('Name', validators=[validators.InputRequired()])
    token = StringField('Token', validators=[validators.InputRequired()])
    submit = SubmitField('Enter Chatroom')
