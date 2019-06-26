# coding=utf-8
from service.action import CommandActionMixin


class OrderOption(object):
    def __init__(self, name, url, login=None):
        self.name = name
        self.url = url
        self.login = login

    def __repr__(self):
        _repr = '%(name)s @ %(url)s' % self.__dict__
        if self.login:
            _repr += '\n' \
                     'credentials: %(login)s' % self.__dict__

        return _repr


class OrdersCommandAction(CommandActionMixin):
    @property
    def help_text(self):
        return 'Displays all order options'

    @property
    def name(self):
        return 'orders'

    def _writer_callback(self, writer, message=None):
        _string = 'The following order options are available:\n'
        _string += '\n'.join(['- %s\n' % option for option in options])
        writer.out(_string)


CONTAINER = 'https://my.1password.com/vaults/rllzgcg4nk5j3axeoedj3vvnku/allitems/'

options = (OrderOption('GoodKarmaCoffee', 'https://http://www.goodkarmacoffee.de/epages/64249863.sf/de_DE/?'
                                          'ObjectPath=/Shops/64249863/Products/057CoMan/SubProducts/057E-0001',
                       CONTAINER + 'ekommw2x4ringiqa2rv5djczd4'),
           )
