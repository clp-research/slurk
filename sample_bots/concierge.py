import requests
import sys
import argparse
import time

from uuid import uuid1
from socketIO_client import SocketIO, BaseNamespace

uri = None
token = None


def message_response(success, error=None):
    if not success:
        print("Could not send message:", error)
        sys.exit(2)

    print("message sent successfully")


# Define the namespace
class ChatNamespace(BaseNamespace):
    tasks = {}

    @staticmethod
    def get_user_task(user):
        task = requests.get(f"{uri}/users/{user['id']}/task", headers={'Authorization': f"Token {token}"})
        if not task.ok:
            print("Could not get user task")
            sys.exit(2)
        return task.json()

    @staticmethod
    def create_room(label, layout=None, read_only=False, show_users=True, show_latency=True):
        room = requests.post(f"{uri}/rooms",
                             headers={'Authorization': f"Token {token}"},
                             json=dict(
                                 name='%s-%s' % (label, uuid1()),
                                 label=label,
                                 layout=layout,
                                 read_only=read_only,
                                 show_users=show_users,
                                 show_latency=show_latency,
                                 static=False)
                             )
        if not room.ok:
            print("Could not create task room")
            sys.exit(3)
        return room.json()

    def on_status(self, status):
        print(status)
        if status['type'] == 'join':
            user = status['user']
            task = self.get_user_task(user)
            if task:
                self.user_task_join(user, task, status['room'])
        elif status['type'] == 'leave':
            user = status['user']
            task = self.get_user_task(user)
            if task:
                self.user_task_leave(user, task)

    def user_task_join(self, user, task, room):
        if not task:
            return

        task_id = task['id']
        user_id = user['id']
        user_name = user['name']

        if task_id not in self.tasks:
            self.tasks[task_id] = {}
        self.tasks[task_id][user_id] = room

        if len(self.tasks[task_id]) == task['num_users']:
            new_room = self.create_room(task['name'], task['layout'])
            print(self.tasks[task_id])
            for user, old_room in self.tasks[task_id].items():
                self.emit("join_room", {'user': user, 'room': new_room['name']}, self.join_room_feedback)
                self.emit("leave_room", {'user': user, 'room': old_room}, self.leave_room_feedback)
            del self.tasks[task_id]
            print("created room:", new_room)
        else:
            self.emit('text', {'msg': f'Hello, {user_name}! I am looking for a partner for you, it might take some '
                               'time, so be patient, please...',
                               'receiver_id': user_id,
                               'room': room}, message_response)

    def user_task_leave(self, user, task):
        if not task:
            return

        task_id = task['id']
        user_id = user['id']
        if task_id in self.tasks and user_id in self.tasks[task_id]:
            del self.tasks[task['id']][user['id']]

    @staticmethod
    def join_room_feedback(success, error=None):
        if not success:
            print("Could not join room:", error)
            sys.exit(4)
        print("user joined room")

    @staticmethod
    def leave_room_feedback(success, error=None):
        if not success:
            print("Could not leave room:", error)
            sys.exit(5)
        print("user left room")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run Concierge bot')
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
                        headers={'Authorization': args.token, 'Name': 'Concierge Bot'},
                        Namespace=ChatNamespace)
    socketIO.wait()
