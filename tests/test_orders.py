# coding=utf-8
from unittest import TestCase

from order_service.orders import OrderOption, order_options_string


class TestOrders(TestCase):
    def test_method_to_string(self):
        self.assertEqual('Shop @ test', '%s' % str(OrderOption('Shop', 'test')))

    def test_method_with_login_to_string(self):
        self.assertEqual('Shop @ test\ncredentials: here',
                         '%s' % str(OrderOption('Shop', 'test', 'here')))

    def test_coffee_in_methods(self):
        self.assertIn('GoodKarmaCoffee @ https://', order_options_string())
