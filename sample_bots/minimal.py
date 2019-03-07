#!/bin/env python

import argparse
import sys
from random import randint

from socketIO_client import SocketIO, BaseNamespace

chat_namespace = None


class ChatNamespace(BaseNamespace):

    def on_joined_room(self, data):
        self.emit("command", {'room': data['room']['id'], 'data': [
        'listen_to', 'new_image_private']})
        self.emit("command", {'room': data['room']['id'], 'data': [
        'listen_to', 'new_image_public']})
        self.emit("command", {'room': data['room']['id'], 'data': [
        'listen_to', 'print_permissions']})
        self.emit(
        "command", {'room': data['room']['id'], 'data': ['listen_to', 'show']})
        self.emit(
        "command", {'room': data['room']['id'], 'data': ['listen_to', 'hide']})
        self.emit(
        "command", {'room': data['room']['id'], 'data': ['listen_to', 'clear']})

    # called when a text message occurred
    def on_message(self, data):
        print("on_message", data)

    # called when a status message occurred
    def on_status(self, data):
        print(data)
        room = data['user']['latest_room']['id']
        if data['type'] == 'join':
            self.emit('text', {
                      'msg': f"{data['user']['name']} has joined the room. Say \"Hello!\" :)", 'room': room})
            self.emit('text', {'msg': f"Hello {data['user']['name']}! I have an image for you:",
                               'receiver': data['user']['sid'], 'room': room})
            self.emit('image', {'image': "https://picsum.photos/400/200?" + str(randint(1, 200000000)),
                                'receiver': data['user']['sid'],
                                'width': 400,
                                'height': 200,
                                'room': room})
        if data['type'] == 'leave':
            self.emit(
                'text', {'msg': f"{data['user']['name']} has left the room :(", 'room': room})

    # called when '/new_image_public' was sent
    def on_new_image_public(self, data):
        print(data)
        self.emit('set_attribute', {
            'room': data['room']['id'],
            'id': "current-image",
            'attribute': "src",
            'value': "https://picsum.photos/400/200?" + str(randint(1, 200000000))
        })

        self.emit('log', {'message': "I have received a command, wohoo \\o/"})
        print(f"new public image requested: {data}")

    # called when '/new_image_private' was sent
    def on_new_image_private(self, data):
        self.emit('set_attribute', {
            'room': data['room']['id'],
            'id': "current-image",
            'attribute': "src",
            'receiver_id': data['user']['id'],
            'value': "https://picsum.photos/400/200?" + str(randint(1, 200000000))
        })

        self.emit('log', {'type': "private_image",
                          'message': "I have received a command, wohoo \\o/"})
        self.emit(
            'log', {'message': "I have received a command, wohoo \\o/ 2"})
        print(f"new private image requested: {data}")

    def on_print_permissions(self, data):
        self.emit("get_permissions", {
        "user": data["user"]["id"], "room": data["user"]["latest_room"]["id"]})

    @staticmethod
    def on_permissions(data):
        user_name = data["user"]["name"]
        room_name = data["room"]["name"]
        permissions = data["permissions"]
        print(f"Permissions of {user_name} for {room_name}: {permissions}")

    def on_show(self, data):
        for parameter in data['data']:
            if parameter == "latency" or parameter == "all":
                self.emit('update_permissions', {"user": data["user"]["id"],
                                                 "room": data["user"]["latest_room"]["id"],
                                                 "latency": True})
            if parameter == "users" or parameter == "all":
                self.emit('update_permissions', {"user": data["user"]["id"],
                                                 "room": data["user"]["latest_room"]["id"],
                                                 "users": True})
            if parameter == "input" or parameter == "all":
                self.emit('update_permissions', {"user": data["user"]["id"],
                                                 "room": data["user"]["latest_room"]["id"],
                                                 "input": True})
            if parameter == "history" or parameter == "all":
                self.emit('update_permissions', {"user": data["user"]["id"],
                                                 "room": data["user"]["latest_room"]["id"],
                                                 "history": True})
            if parameter == "interaction_area" or parameter == "all":
                self.emit('update_permissions', {"user": data["user"]["id"],
                                                 "room": data["user"]["latest_room"]["id"],
                                                 "interaction_area": True})

    def on_hide(self, data):
        for parameter in data['data']:
            if parameter == "latency" or parameter == "all":
                self.emit('update_permissions', {"user": data["user"]["id"],
                                                 "room": data["user"]["latest_room"]["id"],
                                                 "latency": False})
            if parameter == "users" or parameter == "all":
                self.emit('update_permissions', {"user": data["user"]["id"],
                                                 "room": data["user"]["latest_room"]["id"],
                                                 "users": False})
            if parameter == "input" or parameter == "all":
                self.emit('update_permissions', {"user": data["user"]["id"],
                                                 "room": data["user"]["latest_room"]["id"],
                                                 "input": False})
            if parameter == "history" or parameter == "all":
                self.emit('update_permissions', {"user": data["user"]["id"],
                                                 "room": data["user"]["latest_room"]["id"],
                                                 "history": False})
            if parameter == "interaction_area" or parameter == "all":
                self.emit('update_permissions', {"user": data["user"]["id"],
                                                 "room": data["user"]["latest_room"]["id"],
                                                 "interaction_area": False})

    def on_clear(self, data):
        self.emit("clear_chat", {"room": data["user"]["latest_room"]["id"]})


class LoginNamespace(BaseNamespace):
    # verify login status
    def on_login_status(self, data):
        global chat_namespace
        if data["success"]:
            chat_namespace = socketIO.define(ChatNamespace, '/chat')
        else:
            print("Could not login to server:", data['message'])
            sys.exit(1)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Example MinimalBot')
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

        login_namespace.emit('connectWithToken', {
                             'token': args.token, 'name': "minimal bot"})

        socketIO.wait()
