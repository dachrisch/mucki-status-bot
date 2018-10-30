from abc import abstractmethod


class CommandActionMixin(object):

    @abstractmethod
    def callback_command(self, writer):
        """
        :type writer: telegram_service.writer.Writer
        """
        raise NotImplementedError

    def command(self):
        return self.callback_command

    @property
    @abstractmethod
    def name(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def help_text(self):
        raise NotImplementedError
