# coding=utf-8
from service.api import ApiRetriever


class ApiTestRetriever(ApiRetriever):
    class _ApiTestInvoker(object):
        def __init__(self, actual_return):
            self.actual_return = actual_return

        @property
        def get(self):
            return self.actual_return

    def __init__(self, return_dict):
        self.return_dict = return_dict

    def with_method(self, method):
        return ApiTestRetriever._ApiTestInvoker(self.return_dict[method])
