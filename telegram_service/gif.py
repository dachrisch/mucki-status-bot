# coding=UTF-8

from random import randint

from safygiphy import Giphy


class GifRetriever(object):
    def __init__(self, search_provider=Giphy()):
        self.search_provider = search_provider

    def search_gif(self, query, limit=25, offset=0):
        gif = self.search_provider.search(q=query, limit=limit, offset=offset)
        assert gif['meta']['status'] == 200, gif['meta']
        assert gif['pagination']['total_count'] > 0, gif
        return gif

    def random_gif_url(self, query):
        total_gifs = self.search_gif(query=query)
        random_offset = randint(0, int((total_gifs['pagination']['total_count'] - 1) / 25))
        gif = self.search_gif(query=query, limit=25, offset=random_offset)
        random_index = randint(0, gif['pagination']['count'])
        return gif['data'][random_index]['images']['fixed_width']['url']
