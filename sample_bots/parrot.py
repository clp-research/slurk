#!/bin/env python

import argparse
import sys
from random import randint

from socketIO_client import SocketIO, BaseNamespace

chat_namespace = None


class ChatNamespace(BaseNamespace):

    def on_joined_room(self, data):
        self.emit("command", {'room': data['room']['id'], 'data': ['listen_to', 'show_image']})


    # called when a text message occurred
    def on_message(self, data):
        # prevent parroting own messages
        if not data["user"]["name"] == "parrot_bot":
            print("on_message", data)
            message = data['msg']
            room = data["user"]["latest_room"]["id"]
            # send room message
            self.emit("text", {"msg": message, "room":room})

    # called when '/new_image' was sent
    def on_show_image(self, data):
        print(data)
        self.emit('command', {'room': data['room']['id'],
                              'data': ['new_image', "https://picsum.photos/400/200?" + str(randint(1, 200000000))]})
        self.emit('log', {'message': "I have received a command, wohoo \o/"})
        print(f"new public image requested: {data}")

class LoginNamespace(BaseNamespace):
    # verify login status
    def on_login_status(self, data):
        global chat_namespace
        if data["success"]:
            chat_namespace = socketIO.define(ChatNamespace, '/chat')

            # register to commands

        else:
            print("Could not login to server:", data['message'])
            sys.exit(1)


if __name__ == '__main__':

# define required command line arguments
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

# establish connection with socket.io
    with SocketIO(args.chat_host, args.chat_port) as socketIO:
        login_namespace = socketIO.define(LoginNamespace, '/login')

        login_namespace.emit('connectWithToken', {'token': args.token, 'name': "parrot_bot"})

        socketIO.wait()
