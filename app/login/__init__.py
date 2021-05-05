from logging import getLogger

from flask import Blueprint, render_template, redirect, url_for, flash, current_app
from flask_login import login_user

from sqlalchemy.exc import StatementError

login = Blueprint('login', __name__, url_prefix="/login")

from .. import login_manager
from ..models import User, Token
from .forms import LoginForm
from .events import *


@login_manager.user_loader
def load_user(id):
    getLogger("slurk").debug(f"loading user from id {id}")
    return current_app.session.query(User).get(int(id))


@login_manager.request_loader
def load_user_from_request(request):
    token = None
    token_id = request.headers.get('Authorization')
    getLogger("slurk").debug(f"loading user from token {token_id}")

    db = current_app.session
    if token_id:
        try:
            token = db.query(Token).get(token_id)
        except:
            return None
    if not token:
        token_id = request.args.get('token')
        if token_id:
            token = db.query(Token).get(token_id)

    if token and token.valid and token.room:
        if not token.user:
            name = request.headers.get('name')
            if not name:
                name = request.args.get('name')
            if not name:
                name = "<unnamed>"
            token.user = User(name=name, rooms=[token.room])
            db.commit()
        return token.user
    return None


@login.route('/', methods=['GET', 'POST'])
def index():
    token = request.args.get("token", None) if request.method == 'GET' else ""
    name = request.args.get("name", None) if request.method == 'GET' else None

    getLogger("slurk").debug(f"Login with token {token}")

    form = LoginForm()
    if form.validate_on_submit():
        name = form.name.data
        token = form.token.data if form.token.data != '' else None

    if name and token:
        db = current_app.session
        token = current_app.session.query(Token).get(token)
        if token and token.valid:
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
