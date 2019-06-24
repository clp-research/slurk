from socketIO_client import SocketIO, BaseNamespace

import sys
import os
import argparse


# Define the namespace
class ChatNamespace(BaseNamespace):
    # Called when connected
    def __init__(self, io, path):
        super().__init__(io, path)

        self.id = None
        self.emit('ready')

    def on_joined_room(self, data):
        self.id = data['user']

    @staticmethod
    def get_message_response(success, error=None):
        if not success:
            print("Could not send message:", error)
            sys.exit(2)

        print("message sent successfully")

    def on_text_message(self, data):
        if not self.id:
            return

        sender = data['user']['id']
        if sender == self.id:
            return

        print("I got a message, let's send it back!:", data)

        message = data['msg']
        if message.lower() == "hello":
            message = "World!"
        if message.lower() == "ping":
            message = "Pong!"

        if 'room' in data and data['room']:
            self.emit("text", {'room': data['room'], 'msg': message}, self.get_message_response)
        else:
            print("It was actually a private message oO")
            self.emit("text", {'receiver_id': data['user']['id'], 'msg': message}, self.get_message_response)

    def on_image_message(self, data):
        sender = data['user']['id']
        if sender == self.id:
            return

        print("I got an image, let's send it back!:", data)

        if 'room' in data and data['room']:
            self.emit("image", {'room': data['room'],
                                'url': data['url'],
                                'width': data['width'],
                                'height': data['height']},
                      self.get_message_response)
        else:
            print("It was actually a private message oO")
            self.emit("image", {'receiver_id': data['user']['id'],
                                'url': data['url'],
                                'width': data['width'],
                                'height': data['height']},
                      self.get_message_response)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run Echo bot')

    if 'TOKEN' in os.environ:
        token = {'default': os.environ['TOKEN']}
    else:
        token = {'required': True}

    if 'CHAT_HOST' in os.environ:
        chat_host = {'default': os.environ['CHAT_HOST']}
    else:
        chat_host = {'default': 'http://localhost'}

    if 'CHAT_PORT' in os.environ:
        chat_port = {'default': os.environ['CHAT_PORT']}
    else:
        chat_port = {'default': None}

    parser.add_argument('-t', '--token',
                        help='token for logging in as bot (see SERVURL/token)',
                        **token)
    parser.add_argument('-c', '--chat_host',
                        help='full URL (protocol, hostname; ending with /) of chat server',
                        **chat_host)
    parser.add_argument('-p', '--chat_port',
                        type=int,
                        help='port of chat server',
                        **chat_port)
    args = parser.parse_args()

    uri = args.chat_host
    if args.chat_port:
        uri += f":{args.chat_port}"

    sys.stdout.flush()
    uri += "/api/v2"
    token = args.token

    # We pass token and name in request header
    socketIO = SocketIO(args.chat_host, args.chat_port,
                        headers={'Authorization': args.token, 'Name': 'Echo'},
                        Namespace=ChatNamespace)
    socketIO.wait()
