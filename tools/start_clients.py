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

    host = config['server']['host']
    port = config['server']['port']

    if not 'tools' in config.sections():
        config.add_section('tools')

    # web browsers
    browsers = {'browser1':False,'browser2':False}
    for entry in browsers:
        try:
            # run exception if browser is not found or is empty string
            val = config['tools'][entry]
            if len(val) == 0:
                raise Exception('no web browser')
            browsers[entry] = val
        except:
            print ("\nKey '{browser}' is not set in config.ini! Attempting to use default browser. \nPlease specify in the config file which web browser you want to use!".format(browser=entry))
            # write default value for browser to config file
            config['tools'][entry] = ''
            with open('config.ini', 'w') as configfile:
                config.write(configfile)

    # client names
    try:
        # run exception if no client names are found
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
            raise Exception('no secret key')
    except:
        print ('generating secret key')
        # generate secret key with length = 17
        chars = ascii_letters + digits + punctuation.replace('%', '')
        s_key = ''.join(choices(chars, k=17))
        # write secret key to config file
        config['server']['secret-key'] = s_key
        with open('config.ini', 'w') as configfile:
            config.write(configfile)

    return {**browsers, 'client-names':names, 'secret-key':s_key, 'host':host, 'port':port}

def get_client_links(names, key, testroom):
    """ return links to log in as a client """

    # room = 1 -> Waiting Room, room = 2 -> Test Room
    room = 2 if testroom else 1

    links= []
    for i in names:
        name = i
        # retrieve token
        url = 'http://{host}:{port}/token'.format(host=host,port=port)
        s = requests.session()
        r = s.get(url)
        source = lxml.html.document_fromstring(r.content)
        token = source.xpath('//input[@name="csrf_token"]/@value')[0]
        headers = {'Referer': 'http://{host}:{port}/token'.format(host=host,port=port)}
        data = {'csrf_token': token, 'room': room, 'task': '1', 'source': name, 'key': key}
        login_token = s.post(url, data=data, headers=headers).text
        if login_token.endswith('<br />'):
            login_token = login_token[:-6]
        # create link with token
        uris = 'http://{host}:{port}/?name={name}&token={token}'.format(host=host,port=port,name=name,token=login_token)
        links.append(uris)
    return links

parser = argparse.ArgumentParser()
parser.add_argument('--testroom', help='connect clients to test room',
    action='store_true')
args = parser.parse_args()

# get slurk root directory (parent directory of this file)
dir_path = dirname(dirname(realpath(__file__)))
os.chdir(dir_path)

# get information from config file
config_entries = config_entries(dir_path)
browser1 = config_entries['browser1']
browser2 = config_entries['browser2']
try:
    if browser1:
        current_b = browser1
        browser1 = webbrowser.get(browser1)
    if browser2:
        current_b = browser2
        browser2 = webbrowser.get(browser2)
except webbrowser.Error as exc:
    print ("\nError:",exc)
    print ("Invalid browser '{b}'. Please refer to https://docs.python.org/3.7/library/webbrowser.html for supported type names.\n".format(b=current_b))
    exit()
client_names = config_entries['client-names'].split(',')
secret_key = config_entries['secret-key']
host = config_entries['host']
port = config_entries['port']

if __name__ == "__main__":

    # get links for connecting (length of client_names is number of clients)
    try:
        links =  get_client_links(client_names, key=secret_key, testroom=args.testroom)
    except requests.exceptions.ConnectionError as exc:
        print ('\nError: \n', sys.exc_info()[1])
        print ('\nCould not connect to server! Is it running?')
        exit()

    # open generated links using the web browsers specified in config file
    # if browser1 or browser2 is False: use default web browser
    for i,link in list(enumerate(links)):
        try:
            if i%2 == 0:
                browser1.open(link) if browser1 else webbrowser.open(link)
            else:
                browser2.open(link) if browser2 else webbrowser.open(link)
        except Exception as exc:
            print ('\nError: \n', sys.exc_info())
            print ('\nCould not open link in web browser! Try starting the browser first and then re-running the script.')
        sleep(1)
