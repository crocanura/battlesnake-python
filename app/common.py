import bottle
import os

import random
import time
import math
import pickle



class DirectionClass:
	def __init__(self):
		self.left = (-1,0)
		self.right = (1,0)
		self.up = (0,-1)
		self.down = (0,1)

d = DirectionClass()
directions = [d.left, d.right, d.up, d.down]
directionary = {}
directionary['left'] = d.left
directionary['right'] = d.right
directionary['up'] = d.up
directionary['down'] = d.down

def leftright(x):
	if x >= 0:
		return d.right
	return d.left
def updown(y):
	if y >= 0:
		return d.down
	return d.up

vector_sum = lambda x1, y1, x2, y2: (x2+x1, y2+y1)
vector_difference = lambda x1, y1, x2, y2: (x2-x1, y2-y1)
vector_inverted = lambda x, y: (-x, -y)
vector_scaled = lambda x, y, a: (a*x, a*y)
vector_length = lambda x, y: math.sqrt(x*x + y*y)
vector_taxicab = lambda x, y: abs(x)+abs(y)

def closest_direction(tail, head):
	dx = head[0] - tail[0]
	dy = head[1] - tail[1]
	if abs(dx) >= abs(dy):
		return leftright(dx)
	return updown(dy)




def stopwatch(function, params):
	a = time.time()
	function(*params)
	b = time.time()
	return b - a

colour_schemes = {}
colour_schemes['scarlet'] = lambda: (255, random.randint(20,36), 0)
colour_schemes['violet'] = lambda: (random.randint(100,150), 0, 255)
colour_schemes['mint'] = lambda: (0, 255, random.randint(176, 220))
def charcoal():
	i = random.randint(15,50)
	return (i, i, i)
colour_schemes['charcoal'] = charcoal
def colour(cs_name):
	return ''.join('#%02x%02x%02x' % colour_schemes[cs_name]() ).upper()



# Called in Start event
def new_game(request):
	print "Recieved new game request: \n%s" % str(request)

	game_id = request['game_id']
	board_width = request['width']
	board_height = request['height']

	head_url = '%s://%s/static/head.png' % (
	bottle.request.urlparts.scheme,
	bottle.request.urlparts.netloc
	)

	cs_name = random.choice([name for name in colour_schemes])

	return {
		'color': colour(cs_name),
		'taunt': "Colour: %s" % cs_name,
		'head_url': head_url,
		'name': 'battlesnake-python',
		'head_type': 'fang'
	}


# Called in End event
def end_game(request):
	print "Recieved end request: \n%s" % str(request)

	return "200 OK"



