from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

chat = Blueprint('chat', __name__)

from .. import db


@chat.route('/', methods=['GET', 'POST'])
@login_required
def index():
    num_rooms = current_user.rooms.count()
    if num_rooms == 0:
        num_rooms = 1
        current_user.rooms.append(current_user.token.room)
        db.session.commit()

    labels = [room.label for room in current_user.rooms]
    rooms = [room.name for room in current_user.rooms]

    return render_template('chat.html',
                           num_rooms=num_rooms,
                           labels=labels,
                           rooms=rooms,
                           title="slurk - Chat",
                           heading="slurk - Chatroom")
