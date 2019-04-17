from socketIO_client import SocketIO, BaseNamespace

import sys
import argparse

chat_namespace = None


# Define the namespace
class ChatNamespace(BaseNamespace):
    # Called when connected
    def __init__(self, io, path):
        super().__init__(io, path)

        # Ask some general information about this bot (None determines `self`)
        self.emit('get_user', None, self.get_user_response)
        self.emit('get_rooms_by_user', None, self.get_rooms_response)
        self.emit('get_permissions_by_user', None, self.get_permissions_response)

    def on_joined_room(self, room):
        print("joined", room)

    def on_left_room(self, room):
        print("left", room)

    def get_user_response(self, success, user):
        if not success:
            print("Could not retrieve user:", user)
            sys.exit(2)

        print("user: ", user)

    def get_rooms_response(self, success, rooms):
        if not success:
            print("Could not retrieve rooms:", rooms)
            sys.exit(2)

        print("rooms: ", rooms)

    def get_permissions_response(self, success, permissions):
        if not success:
            print("Could not retrieve permissions:", permissions)
            sys.exit(2)

        print("permissions: ", permissions)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run Waiting Room-Bot')
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
                        headers={'Authorization': args.token, 'Name': 'Minimal'},
                        Namespace=ChatNamespace)
    socketIO.wait()
