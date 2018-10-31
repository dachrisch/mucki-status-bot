from abc import abstractmethod, ABC


class ActionMixin(object):

    @property
    @abstractmethod
    def callback_function(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def name(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def help_text(self):
        raise NotImplementedError


class CommandActionMixin(ActionMixin, ABC):
    @property
    def command(self):
        return self.name

    @abstractmethod
    def _writer_callback(self, writer):
        """
        :type writer: telegram_service.writer.Writer
        """
        raise NotImplementedError

    @property
    def callback_function(self):
        return self._writer_callback


class RegexActionMixin(ActionMixin):
    @property
    @abstractmethod
    def pattern(self):
        raise NotImplementedError

    @abstractmethod
    def _writer_callback_with_update(self, update_retriever, writer):
        """
        :type writer: telegram_service.writer.Writer
        """
        raise NotImplementedError

    @property
    def callback_function(self):
        return self._writer_callback_with_update
