from abc import abstractmethod


class CommandActionMixin(object):

    @abstractmethod
    def callback_command(self, writer):
        raise NotImplementedError

    def command(self):
        return self.callback_command

    @property
    @abstractmethod
    def name(self):
        raise NotImplementedError
