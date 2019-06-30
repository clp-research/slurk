from flask_socketio import emit

from .. import socketio


@socketio.on('room_created')
def room_created(data):
    if 'room' not in data:
        return False, "No room specified"
    emit('new_room', {'room': data['room']}, broadcast=True)
    if 'task' in data:
        emit('new_task_room', {'room': data['room'], 'task': data['task']}, broadcast=True)
    return True
