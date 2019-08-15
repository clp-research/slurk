from socketIO_client import SocketIO, BaseNamespace
from time import sleep

import json
import requests
import base64
import sys
import os
import argparse

URI = None
TOKEN = None
TASK_ID = None
OPENVIDU_URL = None
OPENVIDU_AUTH_TOKEN = None


# Define the namespace
class ChatNamespace(BaseNamespace):
    # Called when connected
    def __init__(self, io, path):
        super().__init__(io, path)

        self.sessions = dict()
        self.id = None
        self.emit('ready')

    @staticmethod
    def create_session(session_id):
        resp = requests.post(OPENVIDU_URL + '/api/sessions', verify=False,
                             headers={
                                 "Authorization": OPENVIDU_AUTH_TOKEN,
                                 "Content-Type": "application/json",
                             },
                             data=json.dumps({
                                 "customSessionId": session_id
                             })
                             )

        if resp.status_code == 409:
            return session_id
        elif resp.status_code == 200:
            return json.loads(resp.content)['id']

    def get_user_token(self, room, user_id):
        if user_id == self.id:
            return

        session = self.sessions.get(room)
        if not session:
            return

        user_token = session['tokens'].get(user_id)
        if user_token:
            return user_token

        resp = requests.post(OPENVIDU_URL + '/api/tokens', verify=False,
                             headers={
                                 "Authorization": OPENVIDU_AUTH_TOKEN,
                                 "Content-Type": "application/json",
                             },
                             data=json.dumps({
                                 "session": str(session['id'])
                             })
                             )

        if resp.status_code == 200:
            user_token = json.loads(resp.content)['token']
            session['tokens'][user_id] = user_token
            return user_token

    def on_joined_room(self, data):
        self.id = data['user']
        resp = requests.get(f"{URI}/room/{data['room']}", headers={'Authorization': f"Token {TOKEN}"})
        if resp.status_code == 200:
            room = json.loads(resp.content)
            for id in room['current_users'].keys():
                if self.get_user_token(data['room'], int(id)):
                    self.send_tokens_to_client(data['room'], int(id))

    def on_new_task_room(self, data):
        if data['task'] == TASK_ID:
            self.sessions[data["room"]] = {"id": self.create_session(data['room']), "tokens": dict()}
            self.emit("join_room", {'user': self.id, 'room': data['room']})

    def on_status(self, data):
        if data['type'] != 'join':
            return
        room = data['room']
        user_id = int(data['user']['id'])
        self.get_user_token(room, user_id)
        self.send_tokens_to_client(room, user_id)

    @staticmethod
    def update_client_token_response(success, data=None):
        if not success:
            print("Could not update client token:", data)
            sys.exit(3)
        print("token sent to client")

    def send_tokens_to_client(self, room, user_id):
        session = self.sessions.get(room)
        if not session:
            return
        token = session['tokens'].get(user_id)
        if not token:
            return

        sleep(1)
        self.emit("set_attribute", {"attribute": "value", "value": token, "id": "openvidu-token", 'receiver_id': user_id, 'room': room}, self.update_client_token_response)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run Video bot')

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

    if 'VIDEO_TASK_ID' in os.environ:
        task_id = {'default': os.environ['VIDEO_TASK_ID']}
    else:
        task_id = {'default': None}

    if 'OPENVIDU_SECRET_URL' in os.environ:
        openvidu_url = {'default': os.environ['OPENVIDU_SECRET_URL']}
    else:
        openvidu_url = {'default': 'https://localhost:4443'}

    if 'OPENVIDU_SECRET_KEY' in os.environ:
        openvidu_secret_key = {'default': os.environ['OPENVIDU_SECRET_KEY']}
    else:
        openvidu_secret_key = {'required': True}

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
    parser.add_argument('--task_id',
                        type=int,
                        help='Task to join',
                        **task_id)
    parser.add_argument('--openvidu-url',
                        help='url for the openvidu server',
                        **openvidu_url)
    parser.add_argument('--openvidu-secret-key',
                        help='Secret key for the openvidu server',
                        **openvidu_secret_key)
    args = parser.parse_args()
    TASK_ID = args.task_id
    OPENVIDU_AUTH_TOKEN = 'Basic ' + base64.b64encode(bytes('OPENVIDUAPP:' + args.openvidu_secret_key, 'utf8')).decode(
        'utf8')
    OPENVIDU_URL = args.openvidu_url

    URI = args.chat_host
    if args.chat_port:
        URI += f":{args.chat_port}"

    sys.stdout.flush()
    URI += "/api/v2"
    TOKEN = args.token

    # We pass token and name in request header
    socketIO = SocketIO(args.chat_host, args.chat_port,
                        headers={'Authorization': TOKEN, 'Name': 'Video Bot'},
                        Namespace=ChatNamespace)
    socketIO.wait()
