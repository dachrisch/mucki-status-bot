# coding=UTF-8

import yampy

from config import MEINE_WOCHE_GROUP_ID


class YammerConnector(object):
    def __init__(self):
        self.__yammer = yampy.Yammer(access_token='82740-78pKEYKeuaHyEme0xvzGRg')

    def post_meine_woche(self, message, tags=()):
        message = self.__yammer.messages.create(message, group_id=MEINE_WOCHE_GROUP_ID, topics=tags)

        return message['messages'][0]['web_url']
