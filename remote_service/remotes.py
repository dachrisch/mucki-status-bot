# coding=utf-8
import jsonpickle

from remote_service.service import get_methods
from service.action import CommandActionMixin


class RemoteMethodCommandAction(CommandActionMixin):

    @property
    def help_text(self):
        return 'Displays all options for remote meetings'

    @property
    def name(self):
        return 'remote'

    def _writer_callback(self, writer):
        _string = '---------------------\n'
        _string += '\n'.join(
            ['%s\n---------------------' % method for method in jsonpickle.decode(get_methods())])
        writer.out(_string)
