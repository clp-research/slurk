from socketIO_client import SocketIO, BaseNamespace

import sys
import argparse

chat_namespace = None


# Define the namespace
class ChatNamespace(BaseNamespace):
    id = None

    # Called when connected
    def __init__(self, io, path):
        super().__init__(io, path)

        # Ask some general information about this bot (None determines `self`)
        self.emit('get_user', None, self.get_user_response)

    def get_user_response(self, success, user):
        if not success:
            print("Could not retrieve user:", user)
            sys.exit(2)

        print("user: ", user)
        self.id = user["id"]

    @staticmethod
    def get_message_response(success, error=None):
        if not success:
            print("Could not send message:", error)
            sys.exit(2)

        print("message sent successfully")

    def on_text_message(self, data):
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
    parser.add_argument('token',
                        help='token for logging in as bot (see SERVURL/token)')
    parser.add_argument('-c', '--chat_host',
                        help='full URL (protocol, hostname; ending with /) of chat server',
                        default='http://localhost')
    parser.add_argument('-p', '--chat_port',
                        type=int,
                        help='port of chat server', default=None)
    args = parser.parse_args()

    # We pass token and name in request header
    socketIO = SocketIO(args.chat_host, args.chat_port,
                        headers={'Authorization': args.token, 'Name': 'Echo'},
                        Namespace=ChatNamespace)
    socketIO.wait()
