from common import *

class Cell:

	def __init__(self, x, y):
		self.x = x
		self.y = y

	def xy(self):
		return (self.x, self.y)


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

