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
			snake = board_def.Snake(board, snakedata)
			self.snakes[snake.id()] = snake

			for location in snake.body():
				cell = self.board.get_cell(*location)
				self.snake_cells.append(location)

		self.player = self.snakes[request['you']['id']]
