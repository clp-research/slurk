import requests
import sys
import argparse
import os

from socketIO_client import SocketIO, BaseNamespace

uri = None
token = None


# Define the namespace
class ChatNamespace(BaseNamespace):
    # Called when connected
    def __init__(self, io, path):
        super().__init__(io, path)

        self.emit('ready')

    @staticmethod
    def on_joined_room(data):
        user_id = data['user']
        user = requests.get(f"{uri}/user/{user_id}", headers={'Authorization': f"Token {token}"})

        if not user.ok:
            print("Could not get user")
            sys.exit(2)

        print('Hi! I am "%s"' % user.json()['name'])

        room_name = data['room']
        room = requests.get(f"{uri}/room/{room_name}", headers={'Authorization': f"Token {token}"})
        if not room.ok:
            print("Could not get room")
            sys.exit(3)
        print('I joined "%s"' % room.json()['name'])

        logs = requests.get(f"{uri}/room/{room_name}/logs", headers={'Authorization': f"Token {token}"})
        if not logs.ok:
            print("Could not get logs")
            sys.exit(4)
        print('I found this logs in "%s":' % room.json()['label'])
        for log_entry in logs.json():
            # print(log_entry)
            print("- %s by %s, data:" % (log_entry['event'], log_entry['user']['name']), log_entry['data'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run Minimal bot')

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
                        headers={'Authorization': args.token, 'Name': 'Minimal'},
                        Namespace=ChatNamespace)
    socketIO.wait()
