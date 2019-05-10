from functools import partial
import time

from socketIO_client import SocketIO, BaseNamespace


import sys
import argparse

chat_namespace = None


def message_response(success, error=None):
    if not success:
        print("Could not send message:", error)
        sys.exit(2)

    print("message sent successfully")


# Define the namespace
class ChatNamespace(BaseNamespace):
    tasks = {}

    def on_status(self, status):
        if status['type'] == 'join':
            user = status['user']
            self.emit('get_user_task', user['id'], partial(self.user_task_join, user))
        elif status['type'] == 'leave':
            user = status['user']
            self.emit('get_user_task', user['id'], partial(self.user_task_leave, user))
        print(status)

    def user_task_join(self, user, success, task):
        if not success:
            print("Could not get user task:", task)
            sys.exit(1)
        if not task:
            return

        task_id = task['id']
        user_id = user['id']
        user_name = user['name']

        time.sleep(1.5)
        self.emit('text', {'msg': f'Hello, {user_name}! I am looking for a partner for you, it might take some '
                           'time, so be patient, please...',
                           'receiver_id': user_id}, message_response)

        if task_id not in self.tasks:
            self.tasks[task_id] = set({})
        self.tasks[task_id].add(user_id)

        print(len(self.tasks[task_id]))
        if len(self.tasks[task_id]) == task['num_users']:
            del self.tasks[task_id]
            label = task['name']
            print(f"Now I would like to move you all to {label}, but I'm dumb as Tim did not implemented everything...")

    def user_task_leave(self, user, success, task):
        if not success:
            print("Could not get user task:", task)
            sys.exit(1)
        if not task:
            return

        task_id = task['id']
        user_id = user['id']
        if task_id in self.tasks and user_id in self.tasks[task_id]:
            self.tasks[task['id']].discard(user['id'])


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

    # We pass token and name in request header
    socketIO = SocketIO(args.chat_host, args.chat_port,
                        headers={'Authorization': args.token, 'Name': 'Concierge Bot'},
                        Namespace=ChatNamespace)
    socketIO.wait()
