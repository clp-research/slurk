import os
from os.path import abspath, dirname, basename, realpath
import sys
import argparse
import requests
from lxml.html import document_fromstring
import configparser
import subprocess
import signal
import atexit
from time import sleep
from shutil import copyfile
from string import ascii_letters, digits, punctuation
from random import choices


def config_entries(dir=os.getcwd()):
    """
        retrieve information from config file
        if there's no config.ini in provided directory: copy config.template.ini
        generate secret key if none is found in config.ini
    """
    config = configparser.ConfigParser()
    if 'config.ini' not in os.listdir(dir):
        # copy template file if config.ini doesn't exist
        print ('creating config file')
        copyfile(dir+'/config.template.ini', dir+'/config.ini')
    config.read(dir+'/config.ini')

    host = config['server']['host']
    port = config['server']['port']

    try:
        # run exception if secret-key is not found or is empty string
        s_key = config['server']['secret-key']
        if len(s_key) == 0:
            raise Exception('invalid secret key')
    except:
        print ('generating secret key')
        # generate secret key with length = 17
        chars = ascii_letters + digits + punctuation.replace('%', '')
        s_key = ''.join(choices(chars, k=17))
        # write secret key to config file
        config['server']['secret-key'] = s_key
        with open('config.ini', 'w') as configfile:
            config.write(configfile)

    return {
        'secret-key':s_key,'host':host,'port':port
    }

def get_bot_token(name, key, testroom):
    """
    get a token for connecting a bot
    """
    # get token for test room or waiting room
    room = 2 if testroom else 1

    url = 'http://{host}:{port}/token'.format(host=host,port=port)
    s = requests.session()
    r = s.get(url)
    source = document_fromstring(r.content)
    token = source.xpath('//input[@name="csrf_token"]/@value')[0]
    headers = {'Referer': 'http://{host}:{port}/token'.format(host=host,port=port)}
    data = {'csrf_token': token,
            'room': room,
            'task': '2',
            'reusable': 'y',
            'source': name,
            'key': key
            }
    login_token = s.post(url, data=data, headers=headers).text
    if login_token.endswith('<br />'):
        login_token = login_token[:-6]
    return login_token

parser = argparse.ArgumentParser()
parser.add_argument('bot', nargs='*', help='path to bot file')
parser.add_argument('--testroom', help='connect bots to test room',
    action='store_true')
parser.add_argument('--nopairup', help='do not start pairup bot automatically',
    action='store_true')
args = parser.parse_args()

# get absolute paths for all bot files
bots = [abspath(bot) for bot in args.bot]
# move to slurk root folder
dir_path = dirname(dirname(realpath(__file__)))
os.chdir(dir_path)

if not (args.nopairup or args.testroom):
    # set pairup bot as the first bot to be started
    bots.insert(0, dir_path+'/sample_bots/pairup_bot.py')

# get secret key from config.ini
config_entries = config_entries(dir_path)
secret_key = config_entries['secret-key']
host = config_entries['host']
port = config_entries['port']


if __name__ == "__main__":
    # print basic information
    print ("Directory:",dir_path)
    print ("Bots: ",bots, "\n")
    processes = []
    nullfile = open(os.devnull, "w")

    # start slurk
    server = subprocess.Popen(['python','{path}/chat.py'.format(path=dir_path)])

    # add process id to list of running processes
    processes.append(server.pid)

    # pause to allow server to start before adding bots
    sleep(2)

    # start bots
    for i in bots:
        bot_dir = dirname(i)
        bot_filename = basename(i)
        os.chdir(bot_dir)
        token = get_bot_token(bot_filename, secret_key, args.testroom)

        print ("starting", i, "\ntoken:", token)

        bot_process = subprocess.Popen(['python',bot_filename,token,'--chat_host',host,'--chat_port', port],stdout=nullfile, stderr=nullfile)

        # add process id to list of running processes
        processes.append(bot_process.pid)
        sleep(1)
    # clean up at exit
    def terminate_processes():
        """
        terminate all processes in list of running processes
        """
        print ('terminating processes')
        for process in processes[::-1]:
            os.kill(os.getpgid(process), signal.SIGTERM)
        nullfile.close()

    # register exit handler
    atexit.register(terminate_processes)

    # wait for keyboardinterrupt
    signal.pause()
