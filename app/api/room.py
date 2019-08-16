from flask_socketio import emit
from flask_login import current_user

from ..models.room import Room
from ..models.user import User
from ..api.log import log_event

from .. import socketio


@socketio.on('room_created')
def room_created(data):
    if 'room' not in data:
        return False, "No room specified"
    emit('new_room', {'room': data['room']}, broadcast=True)
    if 'task' in data:
        users = []
        if 'users' in data:
            for user in data['users']:
                user = User.query.get(user)
                if user:
                    users.append({'id': user.id, 'name': user.name})
        emit('new_task_room', {'room': data['room'], 'task': data['task'], 'users': users}, broadcast=True)
    return True


@socketio.on('set_attribute')
def set_attribute(data):
    """
    Sets a javascript attribute to a new value.

    :param data: A dictionary with the following fields:
        - ``attribute``: The attribute to be updated
        - ``value``: The value to be set for the given attribute
        - ``id`` (Optional): The id of the element, which is going to be updated
        - ``class`` (Optional): The class of the element, which is going to be updated
        - ``element`` (Optional): The element type, which is going to be updated. Either ``id``, ``class`` or ``element`` is required.
        - ``receiver_id`` (Optional): Sends the attribute to this receiver only
        - ``room`` (Optional): Sends the attribute to this room. Either ``receiver_id`` or ``room`` is required.
        - ``sender_id`` (Optional): The sender of the message. Defaults to the current user
    """

    sender = current_user if 'sender_id' not in data else User.query.get(data['sender_id'])
    if not sender:
        return False, "sender not found"

    if 'id' not in data and 'class' not in data and 'element' not in data:
        return False, "`set_attribute` requires `id`, `class` or `element`"
    if 'attribute' not in data:
        return False, "`set_attribute` requires `attribute`"
    if 'value' not in data:
        return False, "`set_attribute` requires `value`"
    if 'room' in data:
        room = Room.query.get(data['room'])
        if not room:
            return False, "room not found"
        target = room.name
    else:
        return False, "`set_attribute` requires a `room`"
    if 'receiver_id' in data:
        receiver = User.query.get(data['receiver_id'])
        if not receiver:
            return False, "receiver not found"
        target = receiver.session_id

    log_event("set_attribute", sender, room, data={
                                                     'id': data.get('id'),
                                                     'class': data.get('class'),
                                                     'element': data.get('element'),
                                                     'attribute': data['attribute'],
                                                     'value': data['value']
                                                    })

    emit('attribute_update', {
        'user': sender.id,
        'id': data.get('id'),
        'class': data.get('class'),
        'element': data.get('element'),
        'attribute': data['attribute'],
        'value': data['value']
    }, room=target)
    return True


@socketio.on('set_text')
def set_text(data):
    """
    Sets a html text element  by id to a new value.

    :param data: A dictionary with the following fields:
        - ``id``: The id of the text element, which is going to be updated
        - ``text``: The text to be set
        - ``receiver_id`` (Optional): Sends the text to this receiver only
        - ``room`` (Optional): Sends the text to this room. Either ``receiver_id`` or ``room`` is required.
        - ``sender_id`` (Optional): The sender of the message. Defaults to the current user
    """

    sender = current_user if 'sender_id' not in data else User.query.get(data['sender_id'])
    if not sender:
        return False, "sender not found"

    if 'id' not in data:
        return False, "`set_text` requires `id`"
    if 'text' not in data:
        return False, "`set_text` requires `text`"
    if 'receiver_id' in data:
        receiver = User.query.get(data['receiver_id'])
        if not receiver:
            return False, "receiver not found"
        target = receiver.session_id
    elif 'room' in data:
        room = Room.query.get(data['room'])
        if not room:
            return False, "room not found"
        target = room.name
    else:
        return False, "`set_text` requires `room` or `receiver_id`"

    log_event("set_text", sender, room, data={
                                                'id': data.get('id'),
                                                'text': data['text']
                                                })

    emit('text_update', {
        'user': sender.id,
        'id': data.get('id'),
        'text': data['text'],
    }, room=target)
    return True


@socketio.on('add_class')
def add_class(data):
    """
    Adds the html class to an element by id.

    :param data: A dictionary with the following fields:
        - ``id``: The id of the element, which is going to be updated
        - ``class``: The class to be added
        - ``receiver_id`` (Optional): Adds the class for this receiver only
        - ``room`` (Optional): Adds the class for all __users in this room. Either ``receiver_id`` or ``room`` is required.
        - ``sender_id`` (Optional): The sender of the message. Defaults to the current user
    """

    sender = current_user if 'sender_id' not in data else User.query.get(data['sender_id'])
    if not sender:
        return False, "sender not found"

    if 'id' not in data:
        return False, "`add_class` requires `id`"
    if 'class' not in data:
        return False, "`add_class` requires `class`"
    if 'receiver_id' in data:
        receiver = User.query.get(data['receiver_id'])
        if not receiver:
            return False, "receiver not found"
        target = receiver.session_id
    elif 'room' in data:
        room = Room.query.get(data['room'])
        if not room:
            return False, "room not found"
        target = room.name
    else:
        return False, "`add_class` requires `room` or `receiver_id`"

    emit('class_add', {
        'user': sender.id,
        'id': data.get('id'),
        'class': data['class'],
    }, room=target)
    return True


@socketio.on('remove_class')
def remove_class(data):
    """
    Adds the html class to an element by id.

    :param data: A dictionary with the following fields:
        - ``id``: The id of the element, which is going to be updated
        - ``class``: The class to be added
        - ``receiver_id`` (Optional): Adds the class for this receiver only
        - ``room`` (Optional): Adds the class for all __users in this room. Either ``receiver_id`` or ``room`` is required.
        - ``sender_id`` (Optional): The sender of the message. Defaults to the current user
    """

    sender = current_user if 'sender_id' not in data else User.query.get(data['sender_id'])
    if not sender:
        return False, "sender not found"

    if 'id' not in data:
        return False, "`remove_class` requires `id`"
    if 'class' not in data:
        return False, "`remove_class` requires `class`"
    if 'receiver_id' in data:
        receiver = User.query.get(data['receiver_id'])
        if not receiver:
            return False, "receiver not found"
        target = receiver.session_id
    elif 'room' in data:
        room = Room.query.get(data['room'])
        if not room:
            return False, "room not found"
        target = room.name
    else:
        return False, "`remove_class` requires `room` or `receiver_id`"

    emit('class_removed', {
        'user': sender.id,
        'id': data.get('id'),
        'class': data['class'],
    }, room=target)
    return True
