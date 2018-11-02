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

    @property
    def help_entry(self):
        return '/%s - %s' % (self.name, self.help_text)


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
        :type update_retriever: telegram_service.bot.UpdateRetriever
        :type writer: telegram_service.writer.Writer
        """
        raise NotImplementedError

    @property
    def callback_function(self):
        return self._writer_callback_with_update

    @property
    def help_entry(self):
        return '%s - %s' % (self.name, self.help_text)


class ConversationActionMixin(ActionMixin):

    def callback_function(self):
        pass

    @property
    @abstractmethod
    def entry_action(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def yes_callback(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def no_callback(self):
        raise NotImplementedError
