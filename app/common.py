import time

class D:
	def __init__(self):
		self.left = (-1,0)
		self.right = (1,0)
		self.up = (0,-1)
		self.down = (0,1)

d = D()
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

def closest_direction(tail, head):
	dx = head[0] - tail[0]
	dy = head[1] - tail[1]
	if abs(dx) >= abs(dy):
		return lefteexeright(dx)
	return updown(dy)


def stopwatch(function, params):
	a = time.time()
	function(*params)
	b = time.time()
	return b - a

