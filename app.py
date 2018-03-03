import bottle
import os
import math

from stuff.common import *
import stuff.context_def as context_def

import pickle
import random
import time



last_context = None


# DEVELOPEMENT PAGES

@bottle.route('/data')
def static():
	return (pickle.dumps(last_context))


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

	global last_context
	a = time.time()
	con = context_def.Context(data)
	last_context = con
	# b = time.time()
	# print "Initial setup took %s" % str(b-a) 

	# direction = last_context.harmonic_move()
	
	tauntstr = "I am a snake"

	con.scout_board()

	direction1 = con.actual_greed(last_context.player)

	for snake in con.snake_list:
		if not snake is con.player:
			con.actual_greed(snake)

	con.dfs(con.player)

	# replaces previous
	direction2 = con.best_direction()

	b = time.time()
	print "Total time at server: %s" % str(b-a) 

	if direction2 is None:
		direction = direction1
	else:
		direction = direction2

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
