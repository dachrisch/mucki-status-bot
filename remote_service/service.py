# coding=utf-8
import os

import jsonpickle
from flask import Flask


class RemoteMethod(object):
    def __init__(self, name, remote, login=None):
        self.name = name
        self.remote = remote
        self.login = login


remote_app = Flask(__name__)


@remote_app.route('/remotes/api/v1.0/methods', methods=['GET'])
def get_methods():
    methods = (RemoteMethod('Google', 'https://meet.google.com/upv-baht-nyt'),
               RemoteMethod('Zoom', 'https://zoom.us/j/6787719716', CONTAINER + 'pm6ih2vwgk5emkg2zixymbw24u'),
               RemoteMethod('Talkyoo', 'tel:+494095063183', CONTAINER + 'scvbg54alztpayy5kttbohu3vu'))
    return jsonpickle.encode(methods, unpicklable=False)


CONTAINER = 'https://my.1password.com/vaults/rllzgcg4nk5j3axeoedj3vvnku/allitems/'

if __name__ == '__main__':
    remote_app.run(host=os.getenv('REMOTE_SERVICE_HOST', '0.0.0.0'),
                   port=os.getenv('REMOTE_SERVICE_PORT', 5000))
