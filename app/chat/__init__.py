from flask import Blueprint, render_template, redirect, url_for, current_app
from flask_login import login_required, current_user

chat = Blueprint('chat', __name__)

from .message import *
from .connection import *
from ..api import *


@chat.route('/', methods=['GET', 'POST'])
@login_required
def index():
    db = current_app.session
    if current_user.rooms.count() == 0:
        current_user.rooms.append(current_user.token.room)
        db.commit()

    return render_template('chat.html', title="slurk", token=current_user.token)
