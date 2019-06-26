# coding=utf-8
import os

from service.action import CommandActionMixin
from service.api import ApiRetriever


class RemoteMethodCommandAction(CommandActionMixin):

    def __init__(self):
        self.api_invoker = ApiRetriever('remotes', 'v1.0',
                                        host=os.getenv('REMOTE_SERVICE_HOST', '0.0.0.0'),
                                        port=os.getenv('REMOTE_SERVICE_PORT', 5000))

    @property
    def help_text(self):
        return 'Displays all options for remote meetings'

    @property
    def name(self):
        return 'remote'

    def _writer_callback(self, writer, message=None):
        _string = '---------------------\n'
        _string += '\n'.join(
            ['%s\n---------------------' % method for method in
             RemoteMethodWrapper.from_json_list(self.api_invoker.with_method('methods').get)])
        writer.out(_string)


class RemoteMethodWrapper(object):
    @classmethod
    def from_json_list(cls, json_list):
        return [RemoteMethodWrapper(method_dict) for method_dict in json_list]

    def __init__(self, _dict):
        self.name = _dict['name']
        self.remote = _dict['remote']
        self.login = _dict['login']

    def __repr__(self):
        _repr = '%(name)s - Remote @ %(remote)s' % self.__dict__
        if self.login:
            _repr += '\n' \
                     'credentials: %(login)s' % self.__dict__

        return _repr
