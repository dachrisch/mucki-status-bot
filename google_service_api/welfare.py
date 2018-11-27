# coding=utf-8
import os

from service.action import CommandActionMixin
from service.api import ApiRetriever
from telegram_service.gif import GifRetriever


class WelfareCommandAction(CommandActionMixin):
    def __init__(self):
        self.api_invoker = ApiRetriever('welfare', 'v1.0',
                                        host=os.getenv('WELFARE_SERVICE_HOST', '0.0.0.0'),
                                        port=os.getenv('WELFARE_SERVICE_PORT', 5000))
        self.gif_retriever = GifRetriever()

    def _writer_callback(self, writer):
        writer.out('calculating welfare status of team...\n')
        writer.out_thinking()
        writer.out(self._team_message + '\n')
        writer.out('####### !%s! ########\n' % self._shout_out.upper())
        writer.out_gif(self.gif_retriever.random_gif_url(self._shout_out))

    @property
    def _team_message(self):
        return '\n'.join(
            ['%s is %s' % (member['name'], member['status']) for member in self.api_invoker.with_method('status').get])

    @property
    def _shout_out(self):
        return self.api_invoker.with_method('shout_out').get

    @property
    def name(self):
        return 'howarewe'

    @property
    def help_text(self):
        return 'Displays the welfare status of the team'
