"""
CoLA Bot functionality
"""

# import built-in packages
import os
import sys
import argparse
import random
from itertools import zip_longest
import numpy as np
from threading import Timer

from socketIO_client import SocketIO, BaseNamespace

# import from user-defined packages
import start_bot
import birds_game
import constructed_game
import textcomp_game

# CoLA game global variables
CHAT_NAMESPACE = None
GAMES = []  # game instances for each game room
DEF_PATH = 'cola_data'  # directory path for all the data
# list of game names i.e. real/constructed/text
LIST_OF_GAMES = open('game_list.txt').read().splitlines()
CURRENT_GAMES_AVAILABLE = len(LIST_OF_GAMES)  # number of games available to play
NUM_GAME_TYPES_IN_ROOM = 2  # number of games played in each room
NUM_SUB_QUES = 2 # number of times each game needs to be played
# list of bird categories
LIST_OF_BIRD_GAMES = os.listdir(os.path.join(DEF_PATH, 'images'))
# list of constructed rule names
LIST_OF_CONSTRUCTED_GAMES = open(os.path.join(DEF_PATH, 'rules.txt')).read().splitlines()
# list of text comprehension questions
LIST_OF_TEXTCOMP_GAMES = open(os.path.join(DEF_PATH, 'textcomp.txt')).read().splitlines()

# number of each sub-game example to show per query
NUM_BIRD_RULES = 4  # real-birds
NUM_TEXT_RULES = 1  # text comprehend

GAME_NAME_STRING = []

class Games():
    """
    Cola Bot Game Class
    initialization: constructor, pass room information and add attributes as needed.
    """
    def __init__(self, cola_room, cola_data, game_list_cola, answer_status):
        self.cola_room = cola_room
        self.cola_data = cola_data
        self.game_list_cola = game_list_cola
        self.answer_status = answer_status

    def timer(self, room, *args, minutes=0):
        '''warning players that that have not agreed since they lasted answered - 1 min duration'''
        global CHAT_NAMESPACE
        time_passed = Timer(60, self.timer, [room] + list(args), kwargs={"minutes": minutes + 1})
        if minutes == 2:
            CHAT_NAMESPACE.emit('text', {'msg': 'You both seem to be having a discussion for a long time.'
                                                ' Could you reach an agreement and provide an answer?',
                                                'room': room})
        return time_passed

class ChatNamespace(BaseNamespace):
    """
    Chat Class having CoLA commands #
    """
    def on_new_task_room(self, data):
        """
        This gets called as soon as new task (cola) room is created
        :param data:
        :return:
        """
        global GAMES, CHAT_NAMESPACE

        if data['task']['name'] != 'cola':  # check if the task is 'cola'
            return
        room = data['room']  # room info
        usr_data = data['users']  # both players info
        game_list_cola = []
        answer_status = 0

        print("Joining room", room['name'])
        # create instance of the game class
        game_instance = Games(room, usr_data, game_list_cola, answer_status)
        room_id = data['room']['id']
        game_instance.timer(room_id)
        GAMES.append(game_instance)  # add games

        CHAT_NAMESPACE.emit('join_task', {'room': room['id']})  # join cola and register players
        CHAT_NAMESPACE.basepath = ARGS.image_path  # basepath where all cola data is

        # cola commands #
        CHAT_NAMESPACE.emit("command", {'room': room['id'], 'data': ['listen_to', 'answer']})
        CHAT_NAMESPACE.emit("command", {'room': room['id'], 'data': ['listen_to', 'agree']})

    def on_joined_room(self, data):
        """
        As soon as new task is created, the players join room
        :param data:
        :return:
        """
        global GAMES, CHAT_NAMESPACE
        
        print('CoLA game room is created, now register the players')
        player_name = []
        count_player = 0
        for elem in data['users']:
            if elem['token']['task'] is not None:
                player_name.append(elem['name'])
                count_player += 1

            if count_player == 2:
                self.register_new_players(elem['latest_room']['name'], player_name)

    def register_new_players(self, chat_room, p_names):
        """
        This function is to welcome the players and start the game.
        :param chat_room:
        :param p_names:
        :return:
        """
        global GAMES

        for each_game in GAMES:
            room = each_game.cola_room['name']

            if room == chat_room:
                # welcome message
                self.emit('text', {'msg':'Welcome to the CoLa Game, {} and {}! \n'
                                         ' you will be asked four questions about images or text shown in the'
                                         ' display area on the right side of your screen. Read the question below'
                                         ' properly and kindly start the discussion. You both should'
                                         ' discuss and suggest an answer to each other. Once you both agree on an'
                                         ' answer, the game will proceed further. Please make sure the final answer'
                                         ' should be one sentence description. Use help function in case of any confusion.'
                          .format(p_names[0], p_names[1]),
                                   'room': each_game.cola_room['id']})

                global LIST_OF_GAMES

                # extract games for this room and remove them from the main list #
                if LIST_OF_GAMES and len(LIST_OF_GAMES) < NUM_GAME_TYPES_IN_ROOM:
                    # keep popping till its empty and then re-initialize and pop as needed
                    # if list is non-empty but contains elements less than total games to be
                    # played in a room.
                    while LIST_OF_GAMES:
                        game_types_this_room = LIST_OF_GAMES.pop(0)
                    LIST_OF_GAMES = open('game_list.txt').read().splitlines()
                    num_diff_games = NUM_GAME_TYPES_IN_ROOM - len([game_types_this_room])

                    game_types_this_room = [game_types_this_room] + LIST_OF_GAMES[:num_diff_games]
                    LIST_OF_GAMES = LIST_OF_GAMES[num_diff_games:]
                elif not LIST_OF_GAMES:
                    # list is empty and re-fill
                    LIST_OF_GAMES = open('game_list.txt').read().splitlines()
                    game_types_this_room = LIST_OF_GAMES[:NUM_GAME_TYPES_IN_ROOM]
                    LIST_OF_GAMES = LIST_OF_GAMES[NUM_GAME_TYPES_IN_ROOM:]
                else:
                    # list is non-empty and contains elements more than total games to be
                    # played in a room. Normal Condition.
                    game_types_this_room = LIST_OF_GAMES[:NUM_GAME_TYPES_IN_ROOM]
                    LIST_OF_GAMES = LIST_OF_GAMES[NUM_GAME_TYPES_IN_ROOM:]

                #  repeat the sub-game names i.e. no of each sub-game questions
                each_game.game_list_cola = np.repeat(game_types_this_room, NUM_SUB_QUES)
                each_game.game_list_cola = list(each_game.game_list_cola)

                # start the game - show and start sub-tasks #
                # just to get information on latest room each_game.cola_data[0] #
                self.on_show_and_query(each_game)

    # message to end the game #
    def game_over(self, room):
        global GAMES, CHAT_NAMESPACE
        print(room)
        self.emit('text', {'msg': 'The game is over! Thank you for '
                                  'your participation!', 'room': room})

    # show images and questions and start game #
    def on_show_and_query(self, sub_game):
        """
        Start the game by showing the images and asking sub-questions
        :param data:
        :return:
        """
        global LIST_OF_GAMES, LIST_OF_BIRD_GAMES, LIST_OF_CONSTRUCTED_GAMES, LIST_OF_TEXTCOMP_GAMES

        room_game_type = sub_game.game_list_cola.pop(0)
        print(room_game_type)

        # read the game type: if the game is real/constructed
        if room_game_type == 'real':
            textcomp = 0
            # in each question for a sub-game how many types and their examples to show  #
            if len(LIST_OF_BIRD_GAMES) < NUM_BIRD_RULES:
                # keep popping till its empty and then re-initialize and pop as needed
                # if list is non-empty but contains elements less than total games to be
                # played in a room.
                while LIST_OF_BIRD_GAMES:
                    sub_birds_list = LIST_OF_BIRD_GAMES.pop(0)
                LIST_OF_BIRD_GAMES = os.listdir(os.path.join(DEF_PATH, 'images'))
                num_diff_games = NUM_BIRD_RULES - len(sub_birds_list)
                sub_birds_list = sub_birds_list + LIST_OF_BIRD_GAMES[:num_diff_games]
                LIST_OF_BIRD_GAMES = LIST_OF_BIRD_GAMES[num_diff_games:]
            elif not LIST_OF_BIRD_GAMES:
                # list is empty and re-fill
                LIST_OF_BIRD_GAMES = os.listdir(os.path.join(DEF_PATH, 'images'))
                sub_birds_list = LIST_OF_BIRD_GAMES[:NUM_BIRD_RULES]
                LIST_OF_BIRD_GAMES = LIST_OF_BIRD_GAMES[NUM_BIRD_RULES:]
            else:
                # list is non-empty and contains elements more than total games to be
                # played in a room. Normal Condition.
                sub_birds_list = LIST_OF_BIRD_GAMES[:NUM_BIRD_RULES]
                LIST_OF_BIRD_GAMES = LIST_OF_BIRD_GAMES[NUM_BIRD_RULES:]

            data_dir = os.path.join(DEF_PATH, 'images')
            get_cls_names, get_im_names = birds_game.get_keys(data_dir, sub_birds_list, num_train_img=5)
        elif room_game_type == 'constructed':
            textcomp = 0
            data_dir = os.path.join(DEF_PATH, 'constructed')

            if LIST_OF_CONSTRUCTED_GAMES:
                sub_cons_list = LIST_OF_CONSTRUCTED_GAMES.pop(0)
            else:
                # list is non-empty and contains elements more than total games to be
                # played in a room. Normal Condition.
                LIST_OF_CONSTRUCTED_GAMES = open(os.path.join(DEF_PATH, 'rules.txt')). \
                    read().splitlines()  # list of game names
                sub_cons_list = LIST_OF_CONSTRUCTED_GAMES.pop(0)

            get_cls_names, get_im_names = constructed_game.make_sets(data_dir, sub_cons_list, sub_game.cola_room['name'])

        elif room_game_type == 'textcomp':
            data_dir = 'cola_data/textcomp'
            textcomp = 1

            if LIST_OF_TEXTCOMP_GAMES:
                sub_comp_list = LIST_OF_TEXTCOMP_GAMES.pop(0)
            else:
                # list is non-empty and contains elements more than total games to be
                # played in a room. Normal Condition.
                LIST_OF_TEXTCOMP_GAMES = open(os.path.join(DEF_PATH, 'textcomp.txt')). \
                    read().splitlines()  # list of game names
                sub_comp_list = LIST_OF_TEXTCOMP_GAMES.pop(0)

            get_cls_names, get_im_names = textcomp_game.gen_text_comp(data_dir, sub_comp_list)

        # random names for game categories #
        with open('noun.txt', 'r') as nouns_file:
            NOUNS = nouns_file.read().splitlines()

        random_names = random.sample(NOUNS, len(get_cls_names))

        # for each sub-game #
        all_feat = []
        for cname, get_iname, rname in zip_longest(get_cls_names, get_im_names, random_names):
            # for each class get query and show images
            common_path = os.path.join(data_dir, cname)

            #  check if text comprehension
            if textcomp == 1:
                feature = [' ']
                inames = get_iname
            else:
                feature = [rname]
                inames = [str(os.path.join(common_path, get_iname[i])) for i in range(0, len(get_iname))]

            add_feat = feature + inames
            all_feat.append(add_feat)

        #  For question to be seen on display area.
        rand_name = random.choice(random_names)
        if textcomp == 1:
            ques = 'Based on the series of sentences, a question is asked at the end.' \
                   ' Read the following text carefully and discuss with each other.'

            self.emit('command', {'room': sub_game.cola_room['id'],
                                  'data': ['show_image', all_feat[0], ques]})
        else:
            ques = 'Kindly discuss and reason together about the features of "{}"' \
                   ' and provide a one-sentence description.'.format(rand_name)

            self.emit('command', {'room': sub_game.cola_room['id'],
                                  'data': ['show_image',  all_feat, ques]})

        # query here #
        self.emit('text', {'msg': ques,
                           'room': sub_game.cola_room['id']})

    # players to agree #
    def on_answer(self, data):
        """
        Function to ask partner in the game about one's opinion
        :param data:
        :return:
        """
        global GAMES

        # data here is the information about player whose making the proposal
        chat_room = data['room']['name']
        for each_game in GAMES:
            room = each_game.cola_room['name']

            if room == chat_room:
                all_players = each_game.cola_data

                # take id for other user #
                sent_id = [all_players[i]['id'] for i in range(0, len(all_players))
                           if (data['user']['id'] != all_players[i]['id'])]

                self_id = [all_players[i]['id'] for i in range(0, len(all_players))
                           if (data['user']['id'] == all_players[i]['id'])]

                # timer starts
                room_id = data['room']['id']
                each_game.timer(room_id)

                if data['data']:
                    proposal = " ".join(data['data'][0:])
                    each_game.answer_status = 1

                    # timer starts
                    print('timer starts')
                    room_id = each_game.cola_room['id']
                    tim = each_game.timer(room_id)
                    tim.start()

                    self.emit('text', {'msg': 'Based on the discussion so far, your partner has proposed an answer'
                                              ' shown below. Do you agree with the proposed definition? If not, please'
                                              ' continue the discussion.\n',
                                       'receiver_id': sent_id[0]})
                    self.emit('text', {'msg': proposal, 'receiver_id': sent_id[0]})
                else:
                    self.emit('text', {'msg': 'This command cannot be processed. Answer comes with a description, for example,'
                                              ' /answer This is a... because ...your description here... \n',
                                       'receiver_id': self_id[0]})

    def on_agree(self, data):
        """
        Function where players agree on a answer to the query and
        new query automatically begins or the game ends.
        :param data:
        :return:
        """
        global GAMES

        chat_room = data['room']['name']

        for each_game in GAMES:
            room = each_game.cola_room['name']

            if room == chat_room:
                if each_game.game_list_cola:
                    if each_game.answer_status == 1:
                        # if the game list is non-empty, the game continues.
                        self.on_show_and_query(each_game)

                        # timer cancels
                        print('timer stops')
                        room_id = each_game.cola_room['id']
                        tim = each_game.timer(room_id)
                        tim.cancel()


                        each_game.answer_status = 0
                    else:
                        all_players = each_game.cola_data

                        # take id for other user #
                        self_id = [all_players[i]['id'] for i in range(0, len(all_players))
                                   if (data['user']['id'] == all_players[i]['id'])]

                        self.emit('text',
                                  {'msg': 'This command cannot be processed. You have not provided an answer yet.'
                                          ' You can only progress the game after you provide answers to each other'
                                          ' and then agree on an answer.',
                                   'receiver_id': self_id[0]})
                else:
                    # as soon as the list is empty, game end #
                    self.game_over(data['room']['id'])


class LoginNamespace(BaseNamespace):
    """
    Login endpoint (TCP connection)
    """

    def on_login_status(self, data):
        global CHAT_NAMESPACE
        if data["success"]:
            CHAT_NAMESPACE = socketIO.define(ChatNamespace, '/chat')
        else:
            print("Could not login to server")
            sys.exit(1)

if __name__ == '__main__':
    #TOKEN = start_bot.get_token("game")
    PARSER = argparse.ArgumentParser(description='CoLa-Bot')
    PARSER.add_argument('-token',
                        help='token for logging in as bot ' +
                        '(see SERVURL/token)')
    PARSER.add_argument('-c', '--chat_host',
                        help='full URL (protocol, hostname; ' +
                        'ending with /) of chat server',
                        default='http://localhost')
    PARSER.add_argument('-p', '--chat_port', type=int,
                        help='port of chat server', default=5000)
    PARSER.add_argument('-i', '--image_path',
                        help='path to the cola category images (training and test)',
                        default=DEF_PATH)
    PARSER.add_argument('-f', '--game_flag',
                        help='flag to set the type of game',
                        default=1)
    ARGS = PARSER.parse_args()

    with SocketIO(ARGS.chat_host, ARGS.chat_port) as socketIO:
        LOGIN_NAMESPACE = socketIO.define(LoginNamespace, '/login')
        LOGIN_NAMESPACE.emit('connectWithToken', {'token': ARGS.token, 'name': "CoLA Bot"})
        socketIO.wait()
