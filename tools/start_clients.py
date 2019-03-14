import random
import requests
import webbrowser
import lxml.html
import configparser
import sys
import os
import argparse
from os.path import dirname, realpath
from time import sleep
from shutil import copyfile
from string import ascii_letters, digits, punctuation
from random import choices


def config_entries(dir=os.getcwd()):
    """
        retrieve information from config file
        if there's no config.ini in provided directory: copy config.template.ini
        assign default values to missing entries
    """
    config = configparser.ConfigParser()
    if 'config.ini' not in os.listdir(dir):
        # copy template file if config.ini doesn't exist
        print ('creating config file')
        copyfile(dir+'/config.template.ini', dir+'/config.ini')
    config.read(dir+'/config.ini')

    if not 'tools' in config.sections():
        config.add_section('tools')

    # web browsers
    browsers = {'browser1':False,'browser2':False}
    for entry in browsers:
        try:
            # run exception if browser is not found or is empty string
            val = config['tools'][entry]
            if len(val) == 0:
                raise Exception('invalid web browser')
            browsers[entry] = val
        except:
            print ("\nKey '{browser}' is not set in config.ini! Attempting to use default browser. \nPlease specify in the config file which web browser you want to use!".format(browser=entry))
            # write default value for browser to config file
            config['tools'][entry] = ''
            with open('config.ini', 'w') as configfile:
                config.write(configfile)

    # client names
    try:
        names = config['tools']['client-names']
        if len(names) == 0:
            raise Exception('no client names found')
    except:
        print ('\nNo client names found in config.ini! Setting default names.')
        # write client names to config file
        names = 'client1,client2'
        config['tools']['client-names'] = names
        with open('config.ini', 'w') as configfile:
            config.write(configfile)

    # secret key
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

    return {**browsers, 'client-names':names, 'secret-key':s_key}

def get_client_links(names, key, testroom):
    """ return links to log in as a client """

    # get links for test room or waiting room
    room = 2 if testroom else 1

    links= []
    for i in names:
        name = i
        url = 'http://127.0.0.1:5000/token'
        s = requests.session()
        r = s.get(url)
        source = lxml.html.document_fromstring(r.content)
        token = source.xpath('//input[@name="csrf_token"]/@value')[0]
        headers = {'Referer': 'http://127.0.0.1:5000/token'}
        data = {'csrf_token': token, 'room': room, 'task': '1', 'source': name, 'key': key}
        login_token = s.post(url, data=data, headers=headers).text
        if login_token.endswith('<br />'):
            login_token = login_token[:-6]
        uris = 'http://127.0.0.1:5000/?name={}&token={}'.format(name, login_token)
        links.append(uris)
    return links

parser = argparse.ArgumentParser()
parser.add_argument('--testroom', help='connect clients to test room',
    action='store_true')
args = parser.parse_args()

# use dirname twice to get parent directory of current file
dir_path = dirname(dirname(realpath(__file__)))
os.chdir(dir_path)

# get information from config file
config_entries = config_entries()
browser1 = config_entries['browser1']
if browser1:
    browser1 = webbrowser.get(browser1)
browser2 = config_entries['browser2']
if browser2:
    browser2 = webbrowser.get(browser2)
client_names = config_entries['client-names'].split(',')
secret_key = config_entries['secret-key']

if __name__ == "__main__":
    # get the links (length of client_names is number of clients)
    links =  get_client_links(client_names, key=secret_key, testroom=args.testroom)

    # open generated links using the web browsers specified in config file
    # if browser1 or browser2 is False: use default web browser
    for i,link in list(enumerate(links)):
        if i%2 == 0:
            browser1.open(link) if browser1 else webbrowser.open(link)
        else:
            browser2.open(link) if browser2 else webbrowser.open(link)
        sleep(1)
