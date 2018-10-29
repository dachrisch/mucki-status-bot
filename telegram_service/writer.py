class Writer(object):
    def out(self, message):
        pass


class WriterFactory(object):
    def create(self, *args, **kwargs):
        return Writer()


class TelegramWriter(Writer):
    def __init__(self, bot, chat_id):
        self.bot = bot
        self.__chat_id = chat_id

    def out(self, message):
        self.bot.send_message(self.__chat_id, message,
                              disable_web_page_preview=True)


class TelegramWriterFactory(WriterFactory):
    def __init__(self, bot):
        self.__bot = bot

    def create(self, chat_id):
        return TelegramWriter(self.__bot, chat_id)
