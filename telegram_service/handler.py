# coding=utf-8
from abc import ABC

from telegram.ext import Handler, CommandHandler, RegexHandler, ConversationHandler

from telegram_service.retriever import UpdateRetriever


class ActionHandler(Handler, ABC):
    def __init__(self, action, writer_factory, with_message=False, *args, **kwargs):
        """
        :type action: service.action.ActionMixin
        :type writer_factory: telegram_service.writer.WriterFactory
        """
        Handler.__init__(self, action.callback_function, *args, **kwargs)
        self.action = action
        self.writer_factory = writer_factory
        self.with_message = with_message


class CommandActionHandler(ActionHandler, CommandHandler):
    def __init__(self, action, writer_factory, *args, **kwargs):
        """
        :type action: service.action.CommandActionMixin
        :type writer_factory: telegram_service.writer.WriterFactory
        """
        ActionHandler.__init__(self, action, writer_factory, *args, **kwargs)
        CommandHandler.__init__(self, action.command, action.callback_function)

    def handle_update(self, update, dispatcher):
        """
        :type update: telegram.Update
        :type dispatcher telegram.ext.Dispatcher
        """
        writer = self.writer_factory.create(UpdateRetriever(update).chat_id)

        try:
            if self.with_message:
                message = (update.message or update.edited_message).text
                return self.callback(writer, message)
            else:
                return self.callback(writer)
        except Exception as e:
            writer.out_error(e)
            raise e


class RegexActionHandler(ActionHandler, RegexHandler):
    def __init__(self, action, writer_factory, *args, **kwargs):
        """
        :type action: service.action.RegexActionMixin
        :type writer_factory: telegram_service.writer.WriterFactory
        """
        ActionHandler.__init__(self, action, writer_factory, *args, **kwargs)
        RegexHandler.__init__(self, action.pattern, action.callback_function, *args, **kwargs)

    def handle_update(self, update, dispatcher):
        """
        :type update: telegram.Update
        :type dispatcher telegram.ext.Dispatcher
        """
        update_retriever = UpdateRetriever(update)
        writer = self.writer_factory.create(update_retriever.chat_id)
        try:
            return self.callback(update_retriever, writer)
        except Exception as e:
            writer.out_error(e)
            raise e


class ConversationActionHandler(ActionHandler, ConversationHandler):
    def __init__(self, conversation_action, writer_factory, *args, **kwargs):
        """

        :type conversation_action: ConversationActionMixin
        :type writer_factory: telegram_service.writer.WriterFactory
        """
        ActionHandler.__init__(self, conversation_action, writer_factory, *args, **kwargs)
        ConversationHandler.__init__(self,
                                     entry_points=[
                                         CommandActionHandler(conversation_action.entry_action, writer_factory)],
                                     states={
                                         1: [RegexActionHandler(conversation_action.yes_callback, writer_factory)],
                                     },
                                     fallbacks=[Handler(conversation_action.no_callback)]
                                     )


class MessageAwareCommandActionHandler(CommandActionHandler):
    def __init__(self, action, writer_factory, *args, **kwargs):
        CommandActionHandler.__init__(self, action, writer_factory, with_message=True, *args, **kwargs)
