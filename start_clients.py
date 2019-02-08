import random
import requests
import webbrowser
import lxml.html

link = []

def insert_names_and_tokens():
    for i in ["Dr. John A. Zoidberg"]:#, "Professor Farnsworth"]:
        full_name = i
        url = 'http://127.0.0.1:5000/token'
        s = requests.session()
        r = s.get(url)
        source = lxml.html.document_fromstring(r.content)
        token = source.xpath('//input[@name="csrf_token"]/@value')[0]
        headers = {'Referer': 'http://127.0.0.1:5000/token'}
        data = {'csrf_token': token, 'room': '1', 'task': '1', 'source': '{}'.format(full_name)}
        login_token = s.post(url, data=data, headers=headers).text
        if login_token.endswith('<br />'):
            login_token = login_token[:-6]
        uris = 'http://127.0.0.1:5000/?name={}&token={}'.format(full_name, login_token)
        link.append(uris)
    return link

links = insert_names_and_tokens()

webbrowser.get('chromium-browser').open(links[0])
#webbrowser.get('firefox').open(links[1])
