import os
import argparse
import requests
import lxml.html
from time import sleep

parser = argparse.ArgumentParser()
parser.add_argument('bot', nargs='*')
parser.add_argument('--terminal', default="gnome-terminal")
args = parser.parse_args()

terminal = args.terminal
bots = args.bot
dir_path = os.path.dirname(os.path.realpath(__file__))
dir_virtualenv = "/home/simeon/my_virtualenv/bin"

def get_bot_token(name):
    url = 'http://127.0.0.1:5000/token'
    s = requests.session()
    r = s.get(url)
    source = lxml.html.document_fromstring(r.content)
    token = source.xpath('//input[@name="csrf_token"]/@value')[0]
    headers = {'Referer': 'http://127.0.0.1:5000/token'}
    data = {'csrf_token': token, 'room': '1', 'task': '2', 'reusable': 'y', 'source': '{}'.format(name)}
    login_token = s.post(url, data=data, headers=headers).text
    if login_token.endswith('<br />'):
        login_token = login_token[:-6]
    return login_token

if __name__ == "__main__":

    print ("Directory:",dir_path)
    print ("Terminal:",terminal)
    print ("Bots: ",bots)

    print ("\nstarting chat server")
    os.system('{trmnl} -x bash -c "source {virtualenv}/activate; python3.6 {path}/chat.py"'.format(virtualenv=dir_virtualenv, trmnl=terminal, path=dir_path))
    print ("success")
    sleep(1)

    for i in args.bot:
        token = get_bot_token(i)
        print ("\n\nstarting", i, "\ntoken:", token)
        os.system('{trmnl} -x bash -c "source {virtualenv}/activate; python3.6 {path}/{name} {bot_token} " --title={name}'.format(virtualenv=dir_virtualenv, trmnl=terminal, path=dir_path, name=i, bot_token=token))
        sleep(1)

# os.system('gnome-terminal -x bash -c "source activate_virtualenv.sh;python3.6 chat.py read -n1"')
