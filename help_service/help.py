# coding=utf-8
from service.action import CommandActionMixin


class HelpCommandAction(CommandActionMixin):

    def __init__(self, registry):
        """

        :type registry: telegram_service.bot.BotRegistry
        """
        self.registry = registry

    @property
    def help_text(self):
        return "Prints the help message"

    @property
    def name(self):
        return 'help'

    def _writer_callback(self, writer, message=None):
        text = 'The following commands are available:\n'
        text += '\n'.join(
            [action.help_entry for action in self.registry.registered_actions])
        writer.out(text)


class StartCommandAction(CommandActionMixin):
    def _writer_callback(self, writer, message=None):
        writer.out("I'm the bot of the Südsterne.\nHow can I /help you?")

    @property
    def name(self):
        return 'start'

    @property
    def help_text(self):
        return 'Starts the bot'
