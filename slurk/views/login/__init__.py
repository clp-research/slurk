from flask import (
    render_template,
    redirect,
    url_for,
    flash,
    current_app,
    Blueprint,
    request,
)
from flask_login import login_user

from slurk.extensions.login import login_manager
from slurk.models import User, Token

from .forms import LoginForm


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
    user_id = request.args.get('user') or request.headers.get('user')
    if token_id is None or user_id is None:
        return None

    token_id = token_id.upper().lstrip('BEARER').strip()

    current_app.logger.debug(f"loading user `{user_id}` from token `{token_id}`")

    return current_app.session.query(User).filter_by(token_id=token_id).one_or_none()


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
                flash(
                    "The token is an API token, which can not be used for logging in.",
                    "error",
                )
            elif token.registrations_left != 0:
                if token.registrations_left > 0:
                    token.registrations_left -= 1
                user = User(name=name, token=token, rooms=[token.room])
                db.add(user)
                db.commit()
                login_user(user)
                return redirect(request.args.get('next') or url_for("chat.index"))
            else:
                flash(
                    "The token is either expired, was already used, or isn't correct at all.",
                    "error",
                )
        else:
            flash(
                "The token is either expired, was already used, or isn't correct at all.",
                "error",
            )

    form.token.data = token_id
    form.name.data = name
    return render_template('login.html', form=form, title="slurk - Login")
