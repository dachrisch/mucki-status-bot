# coding=utf-8
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


CONTAINER = 'https://my.1password.com/vaults/rllzgcg4nk5j3axeoedj3vvnku/allitems/'

options = (OrderOption('GoodKarmaCoffee', 'https://shop.strato.de/epages/64249863.sf/de_DE/?'
                                          'ObjectPath=/Shops/64249863/Products/057CoMan/SubProducts/057E-0001'),
           )


def order_options_string():
    _string = 'The following order options are available:\n'
    _string += '\n'.join(['- %s\n' % option for option in options])
    return _string
