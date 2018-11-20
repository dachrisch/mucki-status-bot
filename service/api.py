# coding=utf-8
import jsonpickle
import requests


class ApiRetriever(object):
    class _ApiInvoker(object):
        def __init__(self, url_path, method):
            self.url_path = url_path
            self.method = method

        @property
        def get(self):
            return jsonpickle.decode(requests.get('%(url_path)s/%(method)s' % self.__dict__).text)

    def __init__(self, api_entry, api_version, host='localhost', port=5000):
        self.host = host
        self.port = port
        self.api_entry = api_entry
        self.api_version = api_version

    def with_method(self, method):
        url_path = 'http://%(host)s:%(port)d/%(api_entry)s/api/%(api_version)s' % self.__dict__
        return ApiRetriever._ApiInvoker(url_path, method)
