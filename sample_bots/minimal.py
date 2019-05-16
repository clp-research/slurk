import requests
import sys
import argparse

from socketIO_client import SocketIO, BaseNamespace

uri = None
token = None


# Define the namespace
class ChatNamespace(BaseNamespace):
    # Called when connected
    def __init__(self, io, path):
        super().__init__(io, path)

        self.emit('ready', self.ready_callback)

    @staticmethod
    def ready_callback(success, user_id, rooms):
        if not success:
            print("Could not join chat room")
            sys.exit(1)

        user = requests.get(f"{uri}/users/{user_id}", headers={'Authorization': f"Token {token}"})
        if not user.ok:
            print("Could not get user")
            sys.exit(2)

        print('Hi! I am "%s"' % user.json()['name'])

        for room_name in rooms:
            room = requests.get(f"{uri}/rooms/{room_name}", headers={'Authorization': f"Token {token}"})
            if not room.ok:
                print("Could not get room")
                sys.exit(3)

            print('I joined "%s"' % room.json()['name'])

            logs = requests.get(f"{uri}/rooms/{room_name}/logs", headers={'Authorization': f"Token {token}"})
            if not logs.ok:
                print("Could not get logs")
                sys.exit(4)
            print('I found this logs in "%s":' % room_name)
            for log_entry in logs.json():
                # print(log_entry)
                print("- %s by %s, data:" % (log_entry['event'], log_entry['user']['name']), log_entry['data'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run Minimal bot')
    parser.add_argument('token',
                        help='token for logging in as bot (see SERVURL/token)')
    parser.add_argument('-c', '--chat_host',
                        help='full URL (protocol, hostname; ending with /) of chat server',
                        default='http://localhost')
    parser.add_argument('-p', '--chat_port',
                        type=int,
                        help='port of chat server', default=None)
    args = parser.parse_args()

    uri = args.chat_host
    if args.chat_port:
        uri += f":{args.chat_port}"
    uri += "/api/v2"
    token = args.token

    # We pass token and name in request header
    socketIO = SocketIO(args.chat_host, args.chat_port,
                        headers={'Authorization': args.token, 'Name': 'Minimal'},
                        Namespace=ChatNamespace)
    socketIO.wait()
