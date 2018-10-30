from my_logging import get_logger


class Writer(object):
    def out(self, message):
        """
        :type message: str
        """
        pass

    def out_thinking(self):
        pass

    def out_gif(self, url):
        """
        :type url: str
        """
        pass

    def out_error(self, error):
        """
        :type error: BaseException
        """
        raise error


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
        self.__log = get_logger(self.__class__.__name__)

    def out(self, message):
        self.__log.debug(message)
        self.bot.send_message(self.__chat_id, message,
                              disable_web_page_preview=True)

    def out_thinking(self):
        self.bot.send_chat_action(self.__chat_id, 'typing')

    def out_gif(self, url):
        self.__log.debug(url)
        self.bot.send_document(self.__chat_id, url)

    def out_error(self, error):
        self.__log.exception(error)
        self.bot.send_message(self.__chat_id, '[X] - %s' % error)


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
