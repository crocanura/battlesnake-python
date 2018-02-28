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
	

	def xy(self):
		return (self.x, self.y)


# encapsulates a snake
class Snake:
	def __init__(self, snakedata):
		self.data = snakedata

	def health(self):
		return data['health']
	def length(self):
		return data['length']
	def id(self):
		return data['id']
	def name(self):
		return data['name']

	def bodypart_location(self, index):
		bp = self.data['body']['data'][index]
		return (bp['x']. bp['y'])
	def body(self):
		return [self.bodypart_location(i) for i in range(self.length())]

		


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


	def get_cell(self, x, y):
		return self.grid[y][x]

	def cell_in_dir(self, cell, direction):
		x = cell.x + direction[0]
		y = cell.y + direction[1]

		if 0 <= x and x < self.width:
			if 0 <= y and y < self.height:
				return self.get_cell(x, y)
		return None

	def neighbours(self, cell):
		vals = []
		for direction in directions:
			neighbour = self.cell_in_dir(cell, direction)
			if not neighbour is None:
				vals.append(neighbour)
		return vals





def test():
	b = Board()
	b.set_grid(4, 7)
	c = b.get_cell(3, 4)
	print c.x
	print c.y
	print c.xy()
	c.obj = "hello"

