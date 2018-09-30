#!/bin/env python

import argparse
import sys

from random import randint
from socketIO_client import SocketIO, BaseNamespace

chat_namespace = None
users = {}
self_id = None

def add_user(room, id):
    global users

    room = int(room)
    id = int(id)
    print("adding user", id, "to room", room)

    if room == 1:
        return

    if room not in users:
        users[room] = []
    users[room].append(id)


class ChatNamespace(BaseNamespace):
    @staticmethod
    def on_joined_room(data):
        global users, self_id

        self_id = data['self']['id']

        for user in data['users']:
            if user['id'] != self_id:
                add_user(data['room']['id'], user['id'])

    @staticmethod
    def on_status(data):
        global users
        print("status:", data)

        if data['user']['id'] != self_id:
            add_user(data['room']['id'], data['user']['id'])

    def on_new_task_room(self, data):
        print("hello!!! I have been triggered!")
        print("new task room:", data)
        if data['task']['name'] != 'meetup':
            return

        room = data['room']
        print("Joining room", room['name'])
        self.emit('join_task', {'room': room['id']})
        self.emit("command", {'room': room['id'], 'data': ['listen_to', 'new_image_private']})
        self.emit("command", {'room': room['id'], 'data': ['listen_to', 'new_image_public']})
        self.emit("command", {'room': room['id'], 'data': ['listen_to', 'end_meetup']})

    def on_new_image_public(self, data):
        print("requested new public image:", data)
        self.emit('command', {'room': data['room']['id'],
                              'data': ['new_image', "https://picsum.photos/400/200?" + str(randint(1, 200000000))]})

    def on_new_image_private(self, data):
        print("requested new private image:", data)
        self.emit('command', {'room': data['room']['id'],
                              'data': ['new_image', "https://picsum.photos/400/200?" + str(randint(1, 200000000)),
                                       data['user']['id']]})

    def on_end_meetup(self, data):
        print(data)
        for user in users[data['room']['id']]:
            print(user, "leaving room", data['room']['name'])
            self.emit('leave_room', {'room': data['room']['id'], 'user': user})
            self.emit('join_room', {'room': 1, 'user': user})
        self.emit('leave_room', {'room': data['room']['id']})


class LoginNamespace(BaseNamespace):
    @staticmethod
    def on_login_status(data):
        global chat_namespace
        if data["success"]:
            chat_namespace = socketIO.define(ChatNamespace, '/chat')
        else:
            print("Could not login to server")
            sys.exit(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Example MultiBot')
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
        login_namespace.emit('connectWithToken', {'token': args.token, 'name': "MultiBot"})
        socketIO.wait()
