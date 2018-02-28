import bottle
import os
import math

from common import *
import board

import pickle
import random


# DEVELOPEMENT PAGES

@bottle.route('/data')
def static():
    return (pickle.dumps(data_dump))

# def doit():
#     b = board.Board()
#     b.set_grid(40,40)
#     for col in b.grid:
#         for cell in col:
#             c = b.neighbours(cell)


# @bottle.route('/searchtime')
# def static():
#     return str(stopwatch(doit, ()))


@bottle.route('/')
def static():
    return "the server is running"


@bottle.route('/static/<path:path>')
def static(path):
    return bottle.static_file(path, root='static/')




@bottle.post('/start')
def start():
    data = bottle.request.json
    game_id = data.get('game_id')
    board_width = data.get('width')
    board_height = data.get('height')

    head_url = '%s://%s/static/head.png' % (
        bottle.request.urlparts.scheme,
        bottle.request.urlparts.netloc
    )

    # TODO: Do things with data

    # return {
    #     'color': ''.join('#%02x%02x%02x' % (255, random.randint(30,80), 0)).upper(),
    #     'taunt': tauntstr,
    #     'head_url': head_url,
    #     'name': 'battlesnake-python',
    #     'head_type': 'fang'
    # }
    return new_game(data)


@bottle.post('/move')
def move():
    data = bottle.request.json

    direction = 'up'
    tauntstr = 'wioahdfiuishg'

    return {
        'move': direction,
        'taunt': tauntstr
    }


@bottle.post('/end')
def end():
    data = bottle.request.json

    return end_game(data)


# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()

if __name__ == '__main__':
    bottle.run(
        application,
        host=os.getenv('IP', '127.0.0.1'),
        port=os.getenv('PORT', '8080'),
        debug = True)
