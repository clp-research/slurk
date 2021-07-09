from flask import render_template, current_app, Blueprint
from flask_login import login_required, current_user

from slurk.extensions.login import login_manager

chat = Blueprint("chat", __name__)


def register_blueprints(api):
    api.register_blueprint(chat)


@chat.route("/")
@login_required
def index():
    db = current_app.session

    if current_user.rooms.count() == 0:
        if current_user.token.registrations_left == 0:
            return login_manager.unauthorized()
        else:
            current_user.rooms.append(current_user.token.room)
            db.commit()

    return render_template("chat.html", title="slurk", token=current_user.token.id)
