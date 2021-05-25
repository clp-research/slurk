from logging import getLogger
import uuid

from flask import Blueprint, render_template, redirect, url_for, flash, current_app
from flask_login import login_user

from sqlalchemy.exc import StatementError

from .. import login_manager
from ..models import User, Token
from .forms import LoginForm
from .events import *

login = Blueprint('login', __name__, url_prefix="/login")


@login_manager.user_loader
def load_user(id):
    getLogger("slurk").debug(f"loading user from id {id}")
    return current_app.session.query(User).get(int(id))


@login_manager.request_loader
def load_user_from_request(request):
    token_id = request.headers.get('Authorization') or request.args.get('token')
    if not token_id:
        return None

    getLogger("slurk").debug(f"loading user from token {token_id}")

    if token_id:
        try:
            token_id = uuid.UUID(token_id)
        except ValueError as e:
            getLogger("slurk").debug(f"Invalid token: {e}")
            token_id = None

    db = current_app.session
    token = db.query(Token).filter_by(id=token_id, valid=True).filter(Token.room).one_or_none()

    if not token:
        return None

    if not token.user:
        name = request.headers.get('name')
        if not name:
            name = request.args.get('name')
        if not name:
            name = "<unnamed>"
        token.user = User(name=name, rooms=[token.room])
        db.commit()
    return token.user


@login.route('/', methods=['GET', 'POST'])
def index():
    token = request.args.get("token", None)
    name = request.args.get("name", None)

    form = LoginForm()
    if form.validate_on_submit():
        name = form.name.data
        token = form.token.data

    if token:
        try:
            token = uuid.UUID(token)
        except ValueError as e:
            getLogger("slurk").debug(f'Invalid token "{token}": {e}')
            flash("The token is either expired, was already used, or isn't correct at all.", "error")
            token = None

    if name and token:
        db = current_app.session
        token = db.query(Token).filter_by(id=token, valid=True).filter(Token.room).one_or_none()
        getLogger("slurk").debug(f"Login with token {token}")
        if token:
            if token.room:
                if token.user is None:
                    user = User(name=name, token=token)
                    db.add(user)
                    db.commit()
                else:
                    user = token.user
                login_user(user)
                return redirect(request.args.get('next') or url_for("chat.index"))
            else:
                flash("The token is an API token, which can not be used for logging in.", "error")
        else:
            flash("The token is either expired, was already used, or isn't correct at all.", "error")

    form.token.data = token
    form.name.data = name
    return render_template('login.html', form=form, title="slurk - Login")
