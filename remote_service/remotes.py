class RemoteMethod(object):
    def __init__(self, name, remote, login=None):
        self.name = name
        self.remote = remote
        self.login = login

    def __repr__(self):
        _repr = '%(name)s - Remote @ %(remote)s' % self.__dict__
        if self.login:
            _repr += '\n' \
                     'credentials: %(login)s' % self.__dict__

        return _repr


CONTAINER = 'https://my.1password.com/vaults/rllzgcg4nk5j3axeoedj3vvnku/allitems/'

methods = (RemoteMethod('Google', 'https://meet.google.com/upv-baht-nyt'),
           RemoteMethod('Zoom', 'https://zoom.us/j/6787719716', CONTAINER + 'pm6ih2vwgk5emkg2zixymbw24u'),
           RemoteMethod('Talkyoo', 'tel:+494095063183', CONTAINER + 'scvbg54alztpayy5kttbohu3vu'))


def remote_methods_string():
    _string = '---------------------\n'
    _string += '\n'.join(['%s\n---------------------' % method for method in methods])
    return _string
