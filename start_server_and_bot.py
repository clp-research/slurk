import os
import sys
import argparse
import requests
import lxml.html
import configparser
from time import sleep

platform = sys.platform

if platform == 'darwin':
    import appscript

parser = argparse.ArgumentParser()
parser.add_argument('bot', nargs='*')
args = parser.parse_args()

terminal = "gnome-terminal"
bots = args.bot
dir_path = os.path.dirname(os.path.realpath(__file__))

config = configparser.ConfigParser()
config.read('config.ini')
secret_key = config['server']['secret-key']

def get_bot_token(name, key):
    """ get a token for connecting a bot """
    url = 'http://127.0.0.1:5000/token'
    s = requests.session()
    r = s.get(url)
    source = lxml.html.document_fromstring(r.content)
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
    print ("Terminal:",terminal)
    print ("Bots: ",bots)

    # start slurk in new shell session
    print ("\nstarting chat server")
    if platform == 'linux':
        os.system('{trmnl} -x bash -c "python3.6 {path}/chat.py"'.format(trmnl=terminal, path=dir_path))
    elif platform == 'darwin':
        appscript.app('Terminal').do_script('python3.6 {path}/chat.py'.format(path=dir_path))
    else:
        print ('Could not detect operating system')
    sleep(2)

    # start bots in new shell sessions
    for i in args.bot:
        bot_dir = os.path.abspath(os.path.dirname(i))
        bot_file = os.path.basename(i)
        token = get_bot_token(bot_file, secret_key)
        print ("\n\nstarting", i, "\ntoken:", token)
        if platform == 'linux':
            os.system('{trmnl} -x bash -c "cd {bot_dir}; python3.6 {name} {bot_token}"'.format(trmnl=terminal, bot_dir= bot_dir, name=bot_file, bot_token=token))
        elif platform == 'darwin':
            appscript.app('Terminal').do_script('cd {bot_dir}; python3.6 {name} {bot_token}'.format(bot_dir= bot_dir, name=bot_file, bot_token=token))
        else:
            print ('Could not detect operating system')
            break
        sleep(1)
