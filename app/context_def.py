from common import *
import board_def

class Context:
	def __init__(self, request):
		self.original_request = request

		# self.game_id = request['game_id']

		self.width = request['width']
		self.height = request['height']
		self.board = board_def.Board()
		self.board.set_grid(self.width, self.height)

		# list of tuples
		self.food_cells = []

		for point in request['food']['data']:
			tup = (point['x'], point['y'])
			cell = self.board.get_cell(*tup)
			cell.contains['food'] = True
			self.food_cells.append(cell)

		# snakes indexed by id
		self.snakes = {}
		self.snake_cells = []
		for snakedata in request['snakes']['data']:
			snake = board_def.Snake(snakedata)
			self.snakes[snake.id()] = snake

			count = 0
			for location in snake.body():
				cell = self.board.get_cell(*location)

				if 'snakes' not in cell.contains:
					cell.contains['snakes'] = []
				cell.contains['snakes'].append(tuple([snake, count]))
				count += 1

				self.snake_cells.append(location)

		self.player = self.snakes[request['you']['id']]


	def board_printout(self):

		strings = []
		for row in self.board.grid:
			tmp = ""
			for cell in row:
				if cell.contains == {}:
					tmp += "[] "
				elif 'snakes' in cell.contains:
					l = [snake for snake in cell.contains['snakes']]
					if len(l) > 1:
						tmp += "## "
					elif l[0].bodypart_location(0) == (cell.x, cell.y):
						tmp += "%1dH " % list(self.snakes.keys()).index(l[0].id())
					else:
						tmp += "%1dB " % list(self.snakes.keys()).index(l[0].id())
				elif 'food' in cell.contains:
					tmp += "++ "
				else:
					tmp += "?? "
			strings.append(tmp)

		return strings

