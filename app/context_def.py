from common import *
import board_def
import time

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

		self.snaketionary = {} # by ID
		self.snake_cells = []
		self.snake_list = []
		for snakedata in request['snakes']['data']:
			snake = board_def.Snake(snakedata)
			self.snaketionary[snake.snake_id()] = snake
			self.snake_list.append(snake)

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

		self.player = self.snaketionary[request['you']['id']]


	def harmonic_move(self):
		here = self.player.bodypart_location(0)
		snakepart_weighting = (0,0)
		for snake_id in self.snaketionary:
			for loc in self.snaketionary[snake_id].body():
				vec = vector_difference(*loc+here) # loc+here is the combines tuple
				d = vector_taxicab(*vec)
				if d > 0:
					weight = 1/(vector_length(*vec)*d*4*8)
					weight_vec = vector_scaled(vec[0], vec[1], weight)
					snakepart_weighting = vector_sum(*snakepart_weighting+vec)

		return directionary[closest_direction(0, 0, *vector_inverted(*snakepart_weighting))]


	def location_clear_for_scouting(self, asker, x, y):
		if not self.board.location_is_valid(x, y):
			return False

		cell = self.board.get_cell(x, y)

		if cell.scouting_delay != 0:
			return False

		if asker.snake_id() in cell.contains:
			return False

		return True
		# if cell.scouting_delay == 0:
		# 	return False
		# else:
		# 	return True

	"""returns list of cells""" 
	def neighbours_clear_for_scouting(self, asker, x, y):
		neighbours = self.board.neighbours(x, y)
		vals = []
		for loc in neighbours:
			if self.location_clear_for_scouting(asker, loc[0], loc[1]):
				vals.append(self.board.get_cell(loc[0], loc[1]))
		return vals

	# this algorithm may take a 'long' time
	def scout_board(self):
		start_time = time.time()

		# startup work

		for snake in self.snake_list:

			if snake.scouted != []:
				print "Can't scout. Scouting has already been done"
				return False


			head_cell_location = snake.bodypart_location(0)
			snake.scouted = [[head_cell_location]]
			snake.available_moves = self.neighbours_clear_for_scouting(snake, *head_cell_location)

			# for cell in available_moves:
			# 	cell.scouting_numbers[snake.snake_id()] = 0
			# 	snake.scouted[0].append(cell)
			# 	if 'food' in cell.contains and not snake.scout_tail is None:
			# 		self.board.get_cell(snake.scout_tail).scouting_delay += 1

			# self.board.get_cell(snake.scout_tail).scouting_delay -= 1

			# print "snake.scouted:\n%s\n" % str(snake.scouted)
			# print "snake.available_moves:\n%s\n" % str(snake.available_moves)



		# main scouting loop
		sd = 1 # "scouting distance"
		# N = max([2 * snake.length()])
		while sd <= self.board.width * self.board.height:

			# print "got here"

			num_snakes_that_found_new_cells = 0

			# each snake does a scouting pass
			for snake in self.snake_list:

				# print "%s scouting pass %d" % (snake.name(), sd)

				snake_id = snake.snake_id()
				snake.scouted.append([])

				if not snake.scout_tail is None:
					tail_cell = self.board.get_cell(*snake.scout_tail)

				# print "tail cell: %s" % str([tail_cell.x, tail_cell.y])

				for loc in snake.scouted[sd-1]: # previous pass's cells
					if self.board.get_cell(*loc).scouting_numbers != []:
						continue
						
					next_moves = self.neighbours_clear_for_scouting(snake, loc[0], loc[1])

					# print "next moves: %s" % str([(cell.x,cell.y) for cell in next_moves])

					for move in next_moves:
						if not snake_id in move.scouting_numbers:
							# print 'got here'
							move.scouting_numbers[snake_id] = sd
							# if move not in snake.scouted[sd]:
							snake.scouted[sd].append((move.x, move.y))
							if 'food' in move.contains and not snake.scout_tail is None:
								tail_cell.scouting_delay += 1

				# print "snake.scouted:\n"
				# for line in snake.scouted:
				# 	print line
				# print "size of scouted[sd]%d" % len(snake.scouted[sd])

				if not snake.scout_tail is None:
					tail_cell.scouting_delay -= 1
					if tail_cell.scouting_delay == 0:
						# before cleanup, we must pull in all the snakes that can now
						# reach this cell at this point
						for snake_id in tail_cell.contains:
							pass
						# cleanup
						snake.scout_blocks.remove(snake.scout_tail)
						if snake.scout_blocks == []:
							snake.scout_tail = None
						else:
							snake.scout_tail = snake.scout_blocks[-1]

				# print ""

				if snake.scouted[sd] != []:
					num_snakes_that_found_new_cells += 1

			if num_snakes_that_found_new_cells == 0:
				break

			sd += 1

		print "Farthest scouted: %d" % sd				
		print "Time taken to scout: %s" % str(time.time() - start_time)
		return True





	def board_printout(self):

		strings = []
		for row in self.board.grid:
			tmp = ""
			for cell in row:
				if cell.contains == {}:
					tmp += "[] "
				elif 'snakes' in cell.contains:
					l = [i[0] for i in cell.contains['snakes']]
					if len(l) > 1:
						tmp += "## "
					elif l[0].bodypart_location(0) == (cell.x, cell.y):
						tmp += "%1dH " % self.snake_list.index(l[0])
					else:
						tmp += "%1dB " % self.snake_list.index(l[0])
				elif 'food' in cell.contains:
					tmp += "++ "
				else:
					tmp += "?? "
			strings.append(tmp)

		return strings

	def scouting_printout(self, snake):

		strings = []
		for row in self.board.grid:
			tmp = ""
			for cell in row:
				if snake.snake_id() in cell.scouting_numbers:
					tmp += "%2d " % cell.scouting_numbers[snake.snake_id()]
				else:
					tmp += "[] "
			strings.append(tmp)
		return strings

