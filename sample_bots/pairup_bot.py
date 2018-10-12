#!/bin/env python

from socketIO_client import SocketIO, BaseNamespace

from threading import Timer
import argparse
import random
import string

tasks = {}
REG = {}

# Storage for all timers
notifications = {}

# chat namespace needs to be global to be accessed asynchronously
chat_namespace = None

used_ids = {}


# Notification function with positional arguments for convenience
def notify(user):
    global chat_namespace, notifications

    user_id = user['id']
    name = user['name']

    # Remove the timer, it's not needed anymore
    # del notifications[user_id]

    # Do whatever you want, like sending a text or kick some users
    chat_namespace.emit('text', {'msg': f'Hello, {name}! I am looking for a partner for you, it might take some time, '
                                        f'so be patient, please...',
                                 'receiver_id': user_id})

    notifications[user_id] = Timer(2, give_waiting_room_token, kwargs={"user": user})
    notifications[user_id].start()


def give_waiting_room_token(user):
    global chat_namespace, notifications, REG

    user_id = user['id']
    token = confirmation_code(user, "waiting")
    chat_namespace.emit('text', {'msg': 'Unfortunately, we couldn\'t find a partner for you. You can wait for '
                                        'someone to enter the game, but we will pay only for the time you spent '
                                        'in the room until the moment you receive\ this message.',
                                 'receiver_id': user_id})
    chat_namespace.emit('text', {'msg': 'However, once you leave this room, you have to enter the following token '
                                        'into the field on the HIT webpage. Please enter the token and close the '
                                        'Waiting Room webpage.',
                                 'receiver_id': user_id})
    chat_namespace.emit('text', {'msg': 'Here\'s your token: {}'
                        .format(format(f'{token}' + ''.join(random.choices(string.ascii_uppercase + string.digits,
                                                                           k=6)))),
                                 'receiver_id': user_id})
    del notifications[user_id]
    del REG[user_id]


def confirmation_code(user, gamestate):
    if gamestate == 'waiting':
        token = str(user['token']['uuid']) + "-03"
        chat_namespace.emit('log', {'type': "confirmation_log", 'message': token, 'room': user['latest_room']['id']})
        return token[:-3]  # user shouldn't see appendix / gamestate


class ChatNamespace(BaseNamespace):
    def on_message(self, data):
        print(data)

    def on_joined_room(self, data):
        print(data)
        self.emit("update_info", {'room': data['room']['id'],
                                  'text': "Patience, we are waiting for another player..."})
        self.emit("command", {'room': data['room']['id'], 'data': ['listen_to', 'reset_meetups']})
        self.emit('command', {'room': data['room']['id'],
                              'data': ['new_image', "https://media.giphy.com/media/tXL4FHPSnVJ0A/giphy.gif"]})

    def on_status(self, data):
        global tasks, notifications, REG, used_ids

        user = data['user']
        user_id = user['id']
        task = user['token']['task']
        if not task or user_id in used_ids:
            return
        task_id = task['id']

        print(data)

        if task_id not in tasks:
            tasks[task_id] = {'task': task, 'users': set({}), 'rooms': 0}

        if data['type'] == 'join':
            self.emit("update_info", {'receiver_id': user_id,
                                      'text': "Patience, we are waiting for another player...",
                                      })
            tasks[task_id]['users'].add(user_id)
            if user_id not in REG:
                REG[user_id] = user
                notifications[user_id] = Timer(3, notify, kwargs={"user": user})
                notifications[user_id].start()
        elif data['type'] == 'leave':
            tasks[task_id]['users'].discard(user_id)
        else:
            return

        print(tasks)

        if len(tasks[task_id]['users']) == tasks[task_id]['task']['users']:
            tasks[task_id]['rooms'] += 1
            label = tasks[task_id]['task']['name']
            room = label + " " + str(tasks[task_id]['rooms'])
            notifications[user_id].cancel()
            clients = []
            for user in tasks[task_id]['users']:
                if user and user in notifications:
                    notifications[user].cancel()
                clients.append(user)
                print("move user", user, "to room", room, tasks[task_id]['rooms'])
                used_ids[user] = room
                self.emit("moveUser", {
                    'room': room,
                    'id': user,
                    'message': 'let the game begin!'
                })
            self.emit("open_task_room", {"task": task_id,
                                         "name": room,
                                         "label": label.title(),
                                         "users": clients,
                                         "layout": "meetup-task",
                                         "hide": []})
            tasks[task_id]['users'].clear()

    def on_new_task_room(self, data):
        print("New task room opened: ", data)

    @staticmethod
    def on_reset_meetups(data):
        global used_ids

        used_ids.clear()


class LoginNamespace(BaseNamespace):
    pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run Waiting Room-Bot')
    parser.add_argument('token',
                        help='token for logging in as bot ' +
                             '(see SERVURL/token)')
    parser.add_argument('-c', '--chat_host',
                        help='full URL (protocol, hostname; ' +
                             'ending with /) of chat server',
                        default='http://localhost')
    parser.add_argument('-p', '--chat_port', type=int,
                        help='port of chat server', default=5000)
    args = parser.parse_args()

    with SocketIO(args.chat_host, args.chat_port) as socketIO:
        login_namespace = socketIO.define(LoginNamespace, '/login')
        login_namespace.emit('connectWithToken', {'token': args.token, 'name': "ConciergeBot"})
        chat_namespace = socketIO.define(ChatNamespace, '/chat')
        socketIO.wait()
