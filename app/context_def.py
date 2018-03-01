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

			count = 0 # represents the spot in the body we're at
			for location in snake.body():
				cell = self.board.get_cell(*location)

				if 'snakes' not in cell.contains:
					cell.contains['snakes'] = []
				cell.contains['snakes'].append(tuple([snake, count]))
				
				# prevent snakes from scouting it before it's known to be open
				cell.scouting_delay += 1

				count += 1

				self.snake_cells.append(location)

		self.player = self.snakes[request['you']['id']]


	def harmonic_move(self):
		here = self.player.bodypart_location(0)
		snakepart_weighting = (0,0)
		for id in self.snakes:
			for loc in self.snakes[id].body():
				vec = vector_difference(*loc+here) # loc+here is the combines tuple
				d = vector_taxicab(*vec)
				if d > 0:
					weight = 1/(vector_length(*vec)*d*4*8)
					weight_vec = vector_scaled(vec[0], vec[1], weight)
					snakepart_weighting = vector_sum(*snakepart_weighting+vec)

		return directionary[closest_direction(0, 0, *vector_inverted(*snakepart_weighting))]



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
					elif l[0][0].bodypart_location(0) == (cell.x, cell.y):
						tmp += "%1dH " % list(self.snakes.keys()).index(l[0][0].id())
					else:
						tmp += "%1dB " % list(self.snakes.keys()).index(l[0][0].id())
				elif 'food' in cell.contains:
					tmp += "++ "
				else:
					tmp += "?? "
			strings.append(tmp)

		return strings

	def print_board(self):
		for line in self.board_printout():
			print line

