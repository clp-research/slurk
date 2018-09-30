import json
from calendar import timegm
from datetime import datetime
from os.path import exists, abspath
from os import makedirs


class Logger:
    def __init__(self, file_name):
        self.data = []
        self.file_name = file_name

        if not exists('log'):
            makedirs('log')

    def get_data(self):
        return self.data

    def append(self, data):
        self.data = self.data \
                    + [{**{'timestamp': timegm(datetime.now().utctimetuple()),
                           'timestamp-iso': '{:%Y-%m-%d %H:%M:%S}'.format(datetime.now())}, **data}]
        with open(abspath(self.file_name), 'w') as outfile:
            json.dump(self.data, outfile, indent=4)
