# coding=UTF-8

from safygiphy import Giphy
from random import randint


def search_gif(query, limit=25, offset=0):
    gif = Giphy().search(q=query, limit=limit, offset=offset)
    assert gif['meta']['status'] == 200, gif['meta']
    assert gif['pagination']['total_count'] > 0, r
    return gif


def random_gif_url():
    total_gifs = search_gif(query="awesome")
    random_offset = randint(0, (total_gifs['pagination']['total_count'] - 1) / 25)
    gif = search_gif(query="awesome", limit=25, offset=random_offset)
    random_index = randint(0, gif['pagination']['count'])
    return gif['data'][random_index]['images']['fixed_width']['url']


print random_gif_url()
