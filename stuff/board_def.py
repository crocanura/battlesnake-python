from common import *

# encapsulates a cell within a grid
class Cell:
	def __init__(self, x, y):
		self.x = x
		self.y = y

		self.contains = {}
		# "food": True or False
		# "snakes": [(lennon, 0), (lennon, 2)]
		# where lennon is a snake, and 0 and 2 are the indices of it's parts that fall in the cell
		
		self.scouting_numbers = {}
		# scouting numbers represent how soon the snake with given ID
		# may be able to reach the cell

		self.scouting_delay = 0
		# this represents how many snake parts must move out of the cell
		# before it will be open

		self.scouting_precursors = {}

		self.scout_favour = {}

	def xy(self):
		return (self.x, self.y)

	def __str__(self):
		return "Cell: (%d, %d)" % (self.x, self.y)

	def __repr__(self):
		return str(self)


# encapsulates a snake
class Snake:
	def __init__(self, snakedata):
		self.data = snakedata

		self.scouted = []
		self.available_moves = []

		self.scout_tail = self.bodypart_location(-1)
		self.scout_blocks = self.body()
		self.scouted_distance = len(self.scouted - 1)

		self.pickup = [] # other cells you gain access to

	def health(self):
		return self.data['health']
	def length(self):
		return self.data['length']
	def snake_id(self):
		return self.data['id']
	def name(self):
		return self.data['name']

	def bodypart_location(self, index):
		bp = self.data['body']['data'][index]
		return (bp['x'], bp['y'])
	def body(self):
		return [self.bodypart_location(i) for i in range(self.length())]

	def already_scouted(self, x, y):
		for row in self.scouted:
			if (x, y) in row:
				return True
		return False

	def __str__(self):
		return "Snake: %s" % self.name()

	def __repr__(self):
		return str(self)

		


class Board:

	def __init__(self):
		self.grid = None

	def set_grid(self, width, height):
		self.width = width
		self.height = height
		self.grid = []
		for y in range(height):
			self.grid.append([])
			for x in range(width):
				self.grid[y].append(Cell(x, y))

	
	def location_is_valid(self, x, y):
		if 0 <= x and x < self.width:
			if 0 <= y and y < self.height:
				return True
		return False

	def get_cell(self, x, y):
		return self.grid[y][x]

	# def check.(self, x, y):
	# 	if self.location_is_valid(x, y):
	# 		return 
	# 	return None

	# def cell_in_dir(self, x, y, direction):
	# 	new_x = x + direction[0]
	# 	new_y = y + direction[1]
	# 	return self.get_cell(new_x, new_y)

	def neighbours(self, x, y):
		vals = []
		for direction in directions:
			neighbour = (x + direction[0], y + direction[1])
			if self.location_is_valid(neighbour[0], neighbour[1]):
				vals.append(neighbour)
		return vals




class dfs_cell_node:

	def __init__(self, cell):
		self.cell = cell

		self.parent = None
		self.children = []

		self.distance = 0

	def visited(self, snake):
		# return (snake in self.cell.
		return False

	# def flood_distances(self)





def test():
	b = Board()
	b.set_grid(4, 7)
	c = b.get_cell(3, 4)
	print c.x
	print c.y
	print c.xy()
	c.obj = "hello"

