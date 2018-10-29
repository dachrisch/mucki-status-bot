# coding=utf-8
from service.action import CommandActionMixin


class HelpCommandAction(CommandActionMixin):

    @property
    def name(self):
        return 'help'

    def callback_command(self, writer):
        writer.out("I'm the bot of the *Südsterne* team.\n"
                   'I listen for #highlight messages and otherwise offer the following commands:\n'
                   '/howarewe - get status of team\n'
                   '/show_highlights - displays the currently available highlights\n'
                   '/send_highlights - sends highlights to yammer with current week tag\n'
                   '/remote - shows links to (video-) chat rooms for Südsterne\n'
                   '/orders - view order options\n')


class StartCommandAction(HelpCommandAction):
    @property
    def name(self):
        return 'start'
