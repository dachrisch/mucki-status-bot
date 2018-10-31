# coding=utf-8

from order_service.orders import OrderOption, OrdersCommandAction
from tests.telegram_test_bot import TelegramBotTest


class TestOrders(TelegramBotTest):
    def test_method_to_string(self):
        self.assertEqual('Shop @ test', '%s' % str(OrderOption('Shop', 'test')))

    def test_method_with_login_to_string(self):
        self.assertEqual('Shop @ test\ncredentials: here',
                         '%s' % str(OrderOption('Shop', 'test', 'here')))

    def test_orders_shows_coffee(self):
        self.assert_command_action_responses_with(OrdersCommandAction(),
                                                  'GoodKarmaCoffee @ https://')

    def test_orders_shows_options(self):
        self.assert_command_action_responses_with(OrdersCommandAction(),
                                                  "The following order options are available")
