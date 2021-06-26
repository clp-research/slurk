import uuid

from flask import render_template, redirect, url_for, flash, current_app, Blueprint
from flask_login import login_user

from app.extensions.login import login_manager
from app.models import User, Token

from .forms import LoginForm
from .events import *


login = Blueprint('login', __name__, url_prefix="/login")


def register_blueprints(api):
    api.register_blueprint(login)


@login_manager.user_loader
def load_user(id):
    current_app.logger.debug(f"loading user from id {id}")
    return current_app.session.query(User).get(int(id))


@login_manager.request_loader
def load_user_from_request(request):
    token_id = request.headers.get('Authorization') or request.args.get('token')
    if not token_id:
        return None

    current_app.logger.debug(f"loading user from token {token_id}")

    db = current_app.session
    token = db.query(Token).filter_by(id=token_id).filter(Token.room).one_or_none()

    if not token:
        return None

    name = request.headers.get('name') or request.args.get('name')
    if not name:
        name = '<unnamed>'

    user = token.users.filter_by(name=name, session_id=None).one_or_none()

    if not user:
        user = User(name=name, token=token, rooms=[token.room])
        db.add(user)
        db.commit()
    return user


@login.route('/', methods=['GET', 'POST'])
def index():
    token_id = request.args.get("token")
    name = request.args.get("name")

    form = LoginForm()
    if form.validate_on_submit():
        name = form.name.data
        token_id = form.token.data

    if name and token_id:
        db = current_app.session
        token = db.query(Token).get(token_id)
        current_app.logger.debug(f"Login with token {token_id}")
        if token:
            if token.room is None:
                flash("The token is an API token, which can not be used for logging in.", "error")
            elif token.logins_left != 0:
                if token.logins_left > 0:
                    token.logins_left -= 1
                user = User(name=name, token=token, rooms=[token.room])
                db.add(user)
                db.commit()
                login_user(user)
                return redirect(request.args.get('next') or url_for("chat.index"))
            else:
                flash("The token is either expired, was already used, or isn't correct at all.", "error")
        else:
            flash("The token is either expired, was already used, or isn't correct at all.", "error")

    form.token.data = token_id
    form.name.data = name
    return render_template('login.html', form=form, title="slurk - Login")
