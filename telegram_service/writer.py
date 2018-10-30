class Writer(object):
    def out(self, message):
        """
        :type message: str
        """
        pass


class WriterFactory(object):
    def create(self, *args, **kwargs):
        return Writer()


class TelegramWriter(Writer):
    def __init__(self, bot, chat_id):
        """
        :type bot: telegram.Bot
        :type chat_id: int
        """
        self.bot = bot
        self.__chat_id = chat_id

    def out(self, message):
        """
        :type message: str
        """
        self.bot.send_message(self.__chat_id, message,
                              disable_web_page_preview=True)


class TelegramWriterFactory(WriterFactory):
    def __init__(self, bot):
        """
        :type bot: telegram.Bot
        """
        self.__bot = bot

    def create(self, chat_id):
        """
        :type chat_id: int
        """
        return TelegramWriter(self.__bot, chat_id)
