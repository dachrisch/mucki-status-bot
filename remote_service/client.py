# coding=utf-8
import os

from service.action import CommandActionMixin
from service.api import ApiRetriever


class NewRemoteMethodCommandAction(CommandActionMixin):

    def __init__(self):
        self.api_invoker = ApiRetriever('remotes', 'v1.0',
                                        host=os.getenv('REMOTE_SERVICE_HOST', '0.0.0.0'),
                                        port=os.getenv('REMOTE_SERVICE_PORT', 5000))

    @property
    def help_text(self):
        return 'Displays all options for remote meetings'

    @property
    def name(self):
        return 'remote_new'

    def _writer_callback(self, writer):
        _string = '---------------------\n'
        _string += '\n'.join(
            ['%s\n---------------------' % method for method in self.api_invoker.with_method('methods').get])
        writer.out(_string)
