# coding=UTF-8
import os

import yampy

from config import MEINE_WOCHE_GROUP_ID, ACCESS_TOKEN


class YammerConnector(object):
    def __init__(self):
        self.__yammer = yampy.Yammer(access_token=os.getenv(ACCESS_TOKEN))

    def post_meine_woche(self, message, tags=()):
        message = self.__yammer.messages.create(message, group_id=MEINE_WOCHE_GROUP_ID, topics=tags)
        return message['messages'][0]['web_url']
