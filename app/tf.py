from context_def import *
from common import *
import json
f = open('example_move_requests/%s' % raw_input('request filename: '), 'rb+')
obj = json.load(f)
f.close()

con = None

def a():
	global con
	con = Context(obj)
	return con

def b():
	return con.scout_board()

def c():
	for snake in con.snake_list:
		print "\n %s" % snake.name()
		printlines(con.sc_d_printout(snake))
	print ""
	printlines(con.board_printout())
	print ""
	return None