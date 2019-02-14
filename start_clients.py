import random
import requests
import webbrowser
import lxml.html
import configparser
import sys
from time import sleep

platform = sys.platform

if platform == 'linux':
    # if script is run on linux
    firefox = webbrowser.get('firefox')
    chromium = webbrowser.get('chromium-browser')
    chrome = webbrowser.get('google-chrome')

elif platform == 'darwin':
    # if script is run on osx
    import appscript
    firefox = webbrowser.get('open -a /Applications/Firefox.app %s')
    chrome = webbrowser.get('open -a /Applications/Google\ Chrome.app %s')
    safari = webbrowser.get('open -a /Applications/Safari.app %s')
    opera = webbrowser.get('open -a /Applications/Opera.app %s')
else:
    print ('could not detect operating system')

config = configparser.ConfigParser()
config.read('config.ini')
secret_key = config['server']['secret-key']

def get_client_links(*names, key):
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

    # get the links (number of names == number of clients)
    links =  get_client_links('Dr. John Zoidberg', 'Professor Farnsworth', key=secret_key)

    # open generated links using firefox and chrome
    for i,link in list(enumerate(links)):
        if i%2 == 0:
            firefox.open(link)
        else:
            chrome.open(link)
        sleep(2)
