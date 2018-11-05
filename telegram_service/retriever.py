# coding=utf-8
class AdminRetriever(object):
    def __init__(self, updater, chat_id):
        self.updater = updater
        self.chat_id = chat_id

    @property
    def admin_member(self):
        return list(map(lambda chat_member: chat_member.user.first_name,
                        self.updater.bot.get_chat_administrators(self.chat_id)))


class UpdateRetriever(object):
    def __init__(self, update):
        """

        :type update: telegram.Update
        """
        self._update = update

    @property
    def chat_id(self):
        return self._update.message.chat_id

    @property
    def user(self):
        return self._update.message.from_user.first_name

    @property
    def message(self):
        return self._update.message.text
