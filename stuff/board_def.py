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

		self.node = None


	def xy(self):
		return (self.x, self.y)

	def __str__(self):
		return "Cell: (%d, %d)" % (self.x, self.y)

	def __repr__(self):
		return str(self)


	def originator(self, snake):
		cur = self
		while cur.scouting_numbers[snake] > 1:
			if cur.scouting_precursors[snake] == []:
				return None

			cur = cur.scouting_precursors[snake][0]

		return cur


# encapsulates a snake
class Snake:
	def __init__(self, snakedata):
		self.data = snakedata

		self.scouted = []
		self.available_moves = []

		self.scout_tail = self.bodypart_location(-1)
		self.scout_blocks = self.body()
		self.scouted_distance = len(self.scouted) - 1
		self.tail_cell_by_turn = []

		self.pickup = [] # other cells you gain access to

		self.dfs_root = None
		self.dfs_endpoints = []

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




class cell_node:

	def __init__(self, cell):
		self.cell = cell
		cell.node = self

		self.parent = None
		self.children = []
		self.distance = 0

		self.sums = None

	def add_child(self, new_child):
		if new_child not in self.children:
			self.children.append(new_child)
			new_child.parent = self


	# def originator(self):
	# 	cur = self
	# 	while cur.distance > 1:
	# 		cur = cur.parent
	# 	return cur


	def scouting_intersect(self, snake):

		cur = self
		while snake not in cur.cell.scouting_numbers:
			if cur.parent is None:
				return None
			cur = cur.parent

		return cur




	def calculate_distances(self):
		if self.parent == None:
			self.distance = 0
		else:
			self.distance = self.parent.distance + 1

		for child in self.children:
			child.calculate_distances()

	# always run calculate_distances on the root first
	def calculate_sums(self, snake_list):
		
		# print "Calculating sums for node for %s" % self.cell

		self.sums = {}
		self.sums['favour'] = {}
		for snake in snake_list:
			if snake in self.cell.scout_favour:
				self.sums['favour'][snake] = self.cell.scout_favour[snake]
			else:
				self.sums['favour'][snake] = {"food": 0, "distance": 0}

		self.sums['foodlist'] = []
		if 'food' in self.cell.contains:
			self.sums['foodlist'].append(self.distance)

		
		if not self.parent is None:
			for snake in self.parent.sums['favour']:
				self.sums['favour'][snake]['food'] += self.parent.sums['favour'][snake]['food']
				self.sums['favour'][snake]['distance'] += self.parent.sums['favour'][snake]['distance']

			self.sums['foodlist'].extend(self.parent.sums['foodlist'])
		else:
			print "%s has no parent!" % self


		for child in self.children:
			child.calculate_sums(snake_list)




# class dfs_cell_node:

# 	def __init__(self, cell):
# 		self.cell = cell

# 		self.parent = None
# 		self.children = []

# 		self.distance = 0

# 	def visited(self, snake):
# 		# return (snake in self.cell.
# 		return False

# 	# def flood_distances(self)





def test():
	b = Board()
	b.set_grid(4, 7)
	c = b.get_cell(3, 4)
	print c.x
	print c.y
	print c.xy()
	c.obj = "hello"

