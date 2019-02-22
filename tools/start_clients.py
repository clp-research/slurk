import random
import requests
import webbrowser
import lxml.html
import configparser
import sys
import os
from os.path import dirname, realpath
from time import sleep

# use dirname twice to get parent directory of current file
dir_path = dirname(dirname(realpath(__file__)))
os.chdir(dir_path)

config = configparser.ConfigParser()
config.read('config.ini')
secret_key = config['server']['secret-key']

browser1 = webbrowser.get(config['tools']['browser1'])
browser2 = webbrowser.get(config['tools']['browser2'])
client_names = config['tools']['client_names'].split(',')

def get_client_links(names, key):
    """ return links to log in as a client """
    links= []
    for i in names:
        name = i
        url = 'http://127.0.0.1:5000/token'
        s = requests.session()
        r = s.get(url)
        source = lxml.html.document_fromstring(r.content)
        token = source.xpath('//input[@name="csrf_token"]/@value')[0]
        headers = {'Referer': 'http://127.0.0.1:5000/token'}
        data = {'csrf_token': token, 'room': '1', 'task': '1', 'source': name, 'key': key}
        login_token = s.post(url, data=data, headers=headers).text
        if login_token.endswith('<br />'):
            login_token = login_token[:-6]
        uris = 'http://127.0.0.1:5000/?name={}&token={}'.format(name, login_token)
        links.append(uris)
    return links

if __name__ == "__main__":

    # get the links (length of client_names is number of clients)
    links =  get_client_links(client_names, key=secret_key)

    # open generated links using the web browsers specified in config file
    for i,link in list(enumerate(links)):
        if i%2 == 0:
            browser1.open(link)
        else:
            browser2.open(link)
        sleep(1)
