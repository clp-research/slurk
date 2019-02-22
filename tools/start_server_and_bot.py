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

parser = argparse.ArgumentParser()
parser.add_argument('bot', nargs='*', help='path to bot file')
parser.add_argument('--v', action='store_true', help='verbose output')
args = parser.parse_args()

# get absolute paths for all bot files
bots = [abspath(bot) for bot in args.bot]

# set STDOUT to None or /dev/null, dependent on --v argument
if args.v:
    # verbose
    STDOUT = None
else:
    # stdout and stderr for processes redirected to /dev/null
    STDOUT = open(os.devnull, 'w')

# use dirname twice to move to parent directory of current file (i.e. root folder of slurk)
dir_path = dirname(dirname(realpath(__file__)))
os.chdir(dir_path)

# get secret key from config.ini
config = configparser.ConfigParser()
config.read('config.ini')
secret_key = config['server']['secret-key']

def get_bot_token(name, key):
    """ get a token for connecting a bot """
    url = 'http://127.0.0.1:5000/token'
    s = requests.session()
    r = s.get(url)
    source = document_fromstring(r.content)
    token = source.xpath('//input[@name="csrf_token"]/@value')[0]
    headers = {'Referer': 'http://127.0.0.1:5000/token'}
    data = {'csrf_token': token, 'room': '1', 'task': '2', 'reusable': 'y', 'source': name, 'key': key}
    login_token = s.post(url, data=data, headers=headers).text
    if login_token.endswith('<br />'):
        login_token = login_token[:-6]
    return login_token

if __name__ == "__main__":
    # print basic information
    print ("Directory:",dir_path)
    print ("Bots: ",bots, "\n")
    processes = []

    # start slurk
    print ('starting server')
    server = subprocess.Popen('python {path}/chat.py'.format(path=dir_path), shell=True, stdout=STDOUT, stderr=STDOUT)
    # add process id to list of running processes
    processes.append(server.pid)
    # pause to allow server to start before adding bots
    sleep(2)

    # start bots
    for i in bots:
        bot_dir = dirname(i)
        bot_filename = basename(i)
        os.chdir(bot_dir)
        token = get_bot_token(bot_filename, secret_key)

        print ("\n\nstarting", i, "\ntoken:", token)
        bot_process = subprocess.Popen('python {name} {bot_token}'.format(name=bot_filename, bot_token=token), shell=True, stdout=STDOUT, stderr=STDOUT)
        # add process id to list of running processes
        processes.append(bot_process.pid)
        sleep(1)

# clean up at exit
@atexit.register
def exit_handler():
    print ('closing...')
    # close STDOUT file if script is executed without --v
    if STDOUT:
        STDOUT.close()
    # terminate all processes in list of running processes
    for process in processes[::-1]:
        os.killpg(os.getpgid(process), signal.SIGTERM)

signal.pause()
