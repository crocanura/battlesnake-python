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

		self.snake_cells = []
		self.snake_list = []
		for snakedata in request['snakes']['data']:
			snake = board_def.Snake(snakedata)
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

		for snake in self.snake_list:
			if request['you']['id'] == snake.snake_id():
				self.player = snake



	def location_clear_for_scouting(self, asker, x, y):
		if not self.board.location_is_valid(x, y):
			return False

		cell = self.board.get_cell(x, y)

		if cell.scouting_delay != 0:
			return False

		if asker in cell.scouting_numbers:
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


			head_cell = self.board.get_cell(*snake.bodypart_location(0))
			snake.scouted = [[head_cell]]
			head_cell.scouting_numbers[snake] = 0
			# snake.available_moves = self.neighbours_clear_for_scouting(snake, *head_cell_location)



		# main scouting loop
		sd = 1 # "scouting distance"
		# N = max([2 * snake.length()])
		last_turn = False
		can_advance_tails = True
		food_eaters = []
		while sd <= self.board.width * self.board.height:

			num_snakes_that_found_new_cells = 0

			if food_eaters != []:
				last_turn = True
				for eater in food_eaters:
					if not eater.scout_tail is None:
						self.board.get_cell(*eater.scout_tail).scouting_delay += 1
			

			# ADVANCE SCOUT_TAILS
			if can_advance_tails:
				for scouter in self.snake_list:
					if scouter.scout_tail is None:
						continue

					tail_cell = self.board.get_cell(*scouter.scout_tail)

					tail_cell.scouting_delay -= 1
					if tail_cell.scouting_delay == 0:

						num = 0
						for tup in tail_cell.contains['snakes']:
							if tup[0] is scouter and tup[1] > num:
								num = tup[1]
						if num == 0:
							scouter.scout_tail = None
						else:
							scouter.scout_tail = scouter.bodypart_location(num - 1)



			# each snake does a scouting pass
			for scouter in self.snake_list:

				scouter.scouted.append([])

				# print "#%d scouting pass for %s" % (sd, scouter.name())

				for prev_cell in scouter.scouted[sd-1]: # previous pass's cells
					# prev_cell = self.board.get_cell(*loc)

					# print "found previous cell at %s" % str([prev_cell.x, prev_cell.y])

					# if len(prev_cell.scouting_numbers) > 1: # cell has been scouted by another
					# 	omit_loc = False # by assumption
					# 	for other in prev_cell.scouting_numbers:
					# 		# if other is scouter: # by this snake: stop

					# 		# 	print "cell already scouted:"

					# 		# 	omit_loc = True
					# 		# 	continue

					# 		len1 = scouter.length()
					# 		len2 = other.length()
					# 		if other in food_eaters:
					# 			len2 += 1

					# 		if len2 >= len1: # by a longer snake: stop
					# 			omit_loc = True
					# 			continue

					# 	if omit_loc:
					# 		scouter.scouted[sd-1].remove(prev_cell)
					# 		continue # for scouter; level 4


					next_moves = self.neighbours_clear_for_scouting(scouter, prev_cell.x, prev_cell.y)

					for move in next_moves:

						# scouting numbers may not even be needed
						move.scouting_numbers[scouter] = sd


						scouter.scouted[sd].append(move)

						move.scouting_precursors[scouter] = [] 
						for nearby in self.board.neighbours(move.x, move.y):
							nearby_cell = self.board.get_cell(*nearby)
							if scouter in nearby_cell.scouting_numbers:
								if nearby_cell.scouting_numbers[scouter] < sd:
									move.scouting_precursors[scouter].append(nearby_cell)


						if 'food' in move.contains:
							food_eaters.append(scouter)
							if not scouter.scout_tail is None:
								tail_cell.scouting_delay += 1


				if scouter.scouted[sd] != []:
					num_snakes_that_found_new_cells += 1

			if last_turn:
				can_advance_tails = False

			if num_snakes_that_found_new_cells == 0:
				break

			sd += 1
		sd -= 1


		# remove unsafe squares
		for scouter in self.snake_list:
			for row in snake.scouted:
				marked_for_removal = []
				for cell in row:
					if len(cell.scouting_numbers) > 1: # cell has been scouted by another
						for other in cell.scouting_numbers:

							# print cell.scouting_numbers

							len1 = scouter.length()
							len2 = other.length()
							if other in food_eaters:
								len2 += 1

							if len2 >= len1: # by a mean snake: stop
								marked_for_removal.append(cell)

				for cell in marked_for_removal:
					while cell in row:
						row.remove(cell)



		# trim snake.scouted
		last_row = None
		for snake in self.snake_list:
			for i in range(1, len(snake.scouted)):
				if snake.scouted[-i] != []:
					last_row = -i
					break
		if not last_row is None:
			snake.scouted = snake.scouted[0:last_row+1]

		print "Farthest scouted: %d" % sd				
		print "Time taken to scout: %s" % str(time.time() - start_time)
		return True

	# # a real mess of a function
	# def greed_move(self):
	# 	start_time = time.time()

	# 	move_options = []
	# 	pid = self.player.snake_id()
	# 	for loc in self.player.scouted[-1]:
	# 		end_cell = self.board.get_cell(*loc)
	# 		food = 0
	# 		cur = end_cell
	# 		while True:
	# 			if 'food' in cur.contains:
	# 				food += 1
	# 			if cur.scouting_numbers[pid] == 1:
	# 				break # while
	# 			other_cells = []
	# 			for other_cell in [self.board.get_cell(*n) for n in self.board.neighbours(cur.x, cur.y)]:
	# 				if pid in other_cell.scouting_numbers:
	# 					if other_cell.scouting_numbers[pid] < cur.scouting_numbers[pid]:
	# 						other_cells.append(other_cell)

	# 			# print "cur: %s" % str((cur.x,cur.y))
	# 			# print "other cells: %s" % str([(c.x, c.y) for c in other_cells])
				

	# 			if len(other_cells) == 1:
	# 				cur = other_cells[0]
	# 				continue # while
	# 			max_sn = max([c.scouting_numbers[pid] for c in other_cells])
	# 			other_cells = list(filter(lambda c: c.scouting_numbers[pid] == max_sn, other_cells))
	# 			if len(other_cells) == 1:
	# 				cur = other_cells[0]
	# 				continue # while
	# 			for c in other_cells:
	# 				if 'food' in c.contains:
	# 					cur = c
	# 					break # for
	# 			cur = other_cells[0]
	# 		move_options.append((cur, food))

	# 	most_food = max([tup[1] for tup in move_options])
	# 	for option in move_options:
	# 		if option[1] == most_food:
	# 			dest_cell = option[0]
	# 			a = self.player.bodypart_location(0)
	# 			b = (dest_cell.x, dest_cell.y)
	# 			print "Greed time: %s" % str(time.time() - start_time)
	# 			return directionary[closest_direction(*a+b)]
	# 	# print(move_options)

	# 	return 'left'

	def starving(self, asker):
		return 1 - asker.health()/100

	def greed_priority(self, asker, cell, max_df, max_ff):
		f = cell.scout_favour[asker]['food']/max_ff
		d = cell.scout_favour[asker]['distance']/max_df

		g = 0
		max_snake_length = max(map(lambda s: s.length(), filter(lambda s: not s is self.player,  self.snake_list)))
		l = self.player.length()
		g = 1 + max_snake_length*1.4/l

		s = self.starving(asker)

		return f*s*g+(1.0-s)*d**2

	def actual_greed(self):
		# subtract 1 because of head cell
		# total_scouted = sum([len(line) for line in self.player.scouted]) - 1
		# total_food = len(self.food_cells)
		# if total_food > 0:
		# 	food_bit = 1.0/total_food
		start_time = time.time()

		me = self.player

		for row in me.scouted[::-1][:-1]:
			# if row[0].scouting_numbers[me] == 0:
			# 	break

			for cell in row:

				# print "%s precursors:" % str(cell)
				# print [cell.scouting_precursors]

				if me not in cell.scout_favour:
					cell.scout_favour[me] = {}
					cell.scout_favour[me]['distance'] = 1.0
					cell.scout_favour[me]['food'] = 0.0

				if 'food' in cell.contains:
					cell.scout_favour[me]['food'] += 1.0

				if me not in cell.scouting_precursors:
					continue

				pres = cell.scouting_precursors[me]
				div = float(len(pres))
				if div > 0:
					for pre in pres:
						if me not in pre.scout_favour:
							pre.scout_favour[me] = {}
							pre.scout_favour[me]['distance'] = 1.0 + cell.scout_favour[me]['distance']/div
							pre.scout_favour[me]['food'] = 0.0 + cell.scout_favour[me]['distance']/(12*div)

		end_time = time.time()
		print "Greed time: %s" % str(end_time-start_time)

		# now choose best option
		options = [option for option in me.scouted[1]]
		total_food_favour = sum(cell.scout_favour[me]['food'] for cell in options)
		total_distance_favour = sum(cell.scout_favour[me]['distance'] for cell in options)

		if len(options) == 0:
			return 'left'

		elif len(options) == 1:
			choice = options[0]

		else:
			choice = sorted(options, key= lambda cell: self.greed_priority(me, cell, total_distance_favour, total_food_favour))[-1]

		here = me.bodypart_location(0)
		there = (choice.x, choice.y)
		return directionary[closest_direction(*here+there)]

		return directionary[closest_direction(me.bodypart_location(0)[0], me.bodypart_location(0)[1], self.food_cells[0].x,self.food_cells[0].y)]




	def board_printout(self):

		strings = []
		for row in self.board.grid:
			tmp = ""
			for cell in row:
				if cell.contains == {}:
					tmp += "[    ]"
				elif 'snakes' in cell.contains:
					l = [i[0] for i in cell.contains['snakes']]
					if len(l) > 1:
						tmp += "[ XX ]"
					elif l[0].bodypart_location(0) == (cell.x, cell.y):
						tmp += "[%2d H]" % self.snake_list.index(l[0])
					else:
						tmp += "[%2d B]" % self.snake_list.index(l[0])
				elif 'food' in cell.contains:
					tmp += "[ ++ ]"
				else:
					tmp += "[ ?? ]"
			strings.append(tmp)

		return strings

	def sc_d_printout(self, snake):

		strings = []
		for row in self.board.grid:
			tmp = ""
			for cell in row:
				if snake in cell.scouting_numbers:
					tmp += "[%4d]" % cell.scouting_numbers[snake]
				else:
					tmp += "[    ]"
			strings.append(tmp)
		return strings


	def sc_ff_printout(self, snake):

		strings = []
		for row in self.board.grid:
			tmp = ""
			for cell in row:
				if snake in cell.scout_favour:
					tmp += "[%.2f]" % (cell.scout_favour[snake]['food'] * 10)
				else:
					tmp += "[    ]"
			strings.append(tmp)
		return strings

	def sc_df_printout(self, snake):

		strings = []
		for row in self.board.grid:
			tmp = ""
			for cell in row:
				if snake in cell.scout_favour:
					tmp += "[%.2f]" % cell.scout_favour[snake]['distance']
				else:
					tmp += "[    ] "
			strings.append(tmp)
		return strings

