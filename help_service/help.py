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
        return "The following commands are available:"

    @property
    def name(self):
        return 'help'

    def callback_command(self, writer):
        text = self.help_text + '\n'
        text += '\n'.join([action.help_text for action in self.registry.registered_actions])
        writer.out(text)


class StartCommandAction(CommandActionMixin):
    def callback_command(self, writer):
        writer.out(self.help_text)

    @property
    def name(self):
        return 'start'

    @property
    def help_text(self):
        return "I'm the bot of the *Südsterne* team"
