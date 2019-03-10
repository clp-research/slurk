#!/bin/env python

import argparse
import sys
import threading
import time
import json
import random

from random import randint
from socketIO_client import SocketIO, BaseNamespace

chat_namespace = None
self_id = None
users = {}
TURNS = 4
FILE = "questions_images.json"


def add_user(room, id):
    global users

    room = int(room)
    id = int(id)

    if room == 1:
        return

    if room not in users:
        users[room] = {}
        users[room]['ids'] = []
    users[room]['ids'].append(id)

    # remove id duplicates
    users[room]['ids'] = list(set(users[room]['ids']))
    print("Rooms and Users:", users)


class ChatNamespace(BaseNamespace):

    def on_joined_room(self, data):
        global users, self_id

        self_id = data['self']['id']

        for user in data['users']:
            if user['id'] != self_id:
                add_user(data['room']['id'], user['id'])
        
        # start game as soon as there are two users in one room
        room = data['room']['id']
        if room in users and len(users[room]['ids']) == 2:
            self.welcome_users(data)

    def on_status(self, data):
        global users
        room = data['room']['id']
        if room in users and 'current_image' in users[room]:
            self.on_show_image(room, users[room]['current_image'])

    def on_new_task_room(self, data):
        print("Hello! I have been triggered!")
        if data['task']['name'] != 'meetup':
            return

        room = data['room']
        print("Joining room", room['name'])
        self.emit('join_task', {'room': room['id']})
        self.emit("command", {'room': room['id'], 'data': ['listen_to', 'show']})
        self.emit("command", {'room': room['id'], 'data': ['listen_to', 'hide']})
        self.emit("command", {'room': room['id'], 'data': ['listen_to', 'show_image']})
        self.emit("command", {'room': room['id'], 'data': ['listen_to', 'intercept']})

    # welcome users and start first round
    def welcome_users(self, data):
        global users, TURNS

        room = data['room']['id']
        names = [user['name'] for user in data['users']]
        
        users[room]['names'] = names
        users[room]['rounds'] = TURNS
        users[room]['timer'] = threading.Event()
        
        print(f"Game is starting now in room {room}", 
              f"for the users {names[0]} and {names[1]}.")
        self.emit("text", {"msg": f"Welcome {names[0]} and {names[1]}!", 
                           "room": room})
        self.start_new_round(room)

    # return active and passive user ids
    def active_passive(self, room):
        global users
        return (users[room]['ids'][0], users[room]['ids'][1])

    # return active and passive usernames
    def active_passive_names(self, room):
        global users
        return (users[room]['names'][0], users[room]['names'][1])

    # show/hide input area of the active/passive user
    def show_hide_input_area(self, room):
        active, passive = self.active_passive(room)
        self.on_hide({"data": ["input"], "user": passive, "room": room})
        self.on_show({"data": ["input"], "user": active, "room": room})
        
    # show input area
    def on_show(self, data):
        for parameter in data['data']:
            if parameter == "input" or parameter == "all":
                self.emit('update_permissions', {"user": data["user"],
                                                 "room": data["room"],
                                                 "input": True})

    # hide input area
    def on_hide(self, data):
        for parameter in data['data']:
            if parameter == "input" or parameter == "all":
                self.emit('update_permissions', {"user": data["user"],
                                                 "room": data["room"],
                                                 "input": False})

    # switch the id/name order of the users
    def switch_orders(self, room):
        global users
        users[room]['ids'] = users[room]['ids'][::-1]
        users[room]['names'] = users[room]['names'][::-1]

    # set image in display area
    def on_show_image(self, room_id, url):
        self.emit('set_attribute', {
            'room': room_id,
            'id': "current-image",
            'attribute': "src",
            'value': url
        })

    # start a new round with a new image and ask the main question
    def start_new_round(self, room):
        global users, TURNS
        
        active_id, passive_id = self.active_passive(room)
        active_name, passive_name = self.active_passive_names(room)
        
        self.emit("text", {"msg": f"It is your turn now, {active_name}.", 
                           "receiver_id": active_id})
        self.emit("text", {"msg": f"It is your partner's turn now, {passive_name}.", 
                           "receiver_id": passive_id})
        
        question, image_url, forbidden_words = self.get_data()
        forbidden = f"Don't use the following words: {forbidden_words}"
        users[room]['forbidden'] = forbidden_words.split(", ")
        users[room]['current_image'] = image_url

        self.on_show_image(room, image_url)
        self.show_hide_input_area(room)
        self.emit("text", {"msg": question, "receiver_id": active_id})
        self.emit("text", {"msg": forbidden, "receiver_id": active_id})

        # if it's the first round then call the function which will
        # keep the passive user on line
        if users[room]['rounds'] == TURNS:
            self.keep_on_line(room)

    # choose question, image-url and forbidden words from example file
    def get_data(self):
        global FILE
        with open(FILE) as f:
            data = json.load(f)
        chosen = random.choice([data[element] for element in data])
        return chosen['question'], chosen['image_url'], chosen['forbidden_words']

    # keep passive user on line (call this function every 15 seconds)
    def keep_on_line(self, room):
        global users
        event = users[room]['timer']
        messages = ['Your partner is thinking...', 'Patience...', 
                    'Just wait a little more..', 'Please wait for your turn..']
        if type(event) != bool:
            active, passive = self.active_passive(room)
            self.emit('text', {'msg': random.choice(messages), 
                               'receiver_id': passive})
            threading.Timer(15, self.keep_on_line, [room]).start()

    # intercept messages and check them 
    def on_intercept(self, data):
        global users
        
        print("Intercepted message:", data['data'][0])
        answer = data['data'][0]
        room = data["user"]["latest_room"]["id"]
        receiver = data['user']['id']
        
        if users[room]['rounds'] == 1:
            # stop the timer and end the game
            users[room]['timer'] = users[room]['timer'].is_set()
            self.emit("text", {"msg": "It's over, bye!", "room": room})
            self.on_hide({"data": ["input"], "user": receiver, "room": room})
            print("Game is over!")
        elif users[room]['rounds'] % 2 == 0:
            test = self.check_answer(room, answer)
            if test == False:
                self.emit("text", {"msg": "Invalid reply. Don't use the forbidden words.", 
                                   "receiver_id": receiver})
            else:
                users[room]['rounds'] -= 1
                self.emit("text", {"msg": "Your answer is accepted.", 
                                   "receiver_id": receiver})
                self.following_round(room, answer)
        else:
            users[room]['rounds'] -= 1
            self.emit("text", {"msg": "Okay, we'll start the next round now!", 
                               "room": room})
            self.start_new_round(room)

    # check user's answer    
    def check_answer(self, room, answer):
        global users
        for word in users[room]['forbidden']:
            if word in answer:
                return False

    # continue with the follow-up question
    def following_round(self, room, answer):
        global users
        self.switch_orders(room)
        self.show_hide_input_area(room)
        active, passive = self.active_passive(room)
        question = f"Which object do you think was referred to with: '{answer}'"
        self.emit("text", {"msg": "It's your partner's turn now.", "receiver_id": passive})
        self.emit("text", {"msg": "It's your turn now.", "receiver_id": active})
        self.emit("text", {"msg": question, "receiver_id": active})


class LoginNamespace(BaseNamespace):
    @staticmethod
    def on_login_status(data):
        global chat_namespace
        if data["success"]:
            chat_namespace = socketIO.define(ChatNamespace, '/chat')
        else:
            print("Could not login to server")
            sys.exit(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='TurnTakingBot')
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
                             'token': args.token, 'name': "TTBot"})
        socketIO.wait()

