from common import *
import board_def
from board_def import cell_node
import time
from collections import deque



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

			if snake.health <= 0:
				continue #ignore dead snakes

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
		while sd <= 20:

			num_snakes_that_found_new_cells = 0

			# if food_eaters != []:
			# 	last_turn = True
			for eater in food_eaters:
				if not eater.scout_tail is None:
					self.board.get_cell(*eater.scout_tail).scouting_delay += 1
			food_eaters = []

			# ADVANCE SCOUT_TAILS
			if can_advance_tails:
				for scouter in self.snake_list:
					if scouter.scout_tail is None:
						scouter.tail_cell_by_turn.append(tail_cell)
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

					scouter.tail_cell_by_turn.append(tail_cell)



			# each snake does a scouting pass
			for scouter in self.snake_list:

				scouter.scouted.append([])

				# print "#%d scouting pass for %s" % (sd, scouter.name())

				for prev_cell in scouter.scouted[sd-1]: # previous pass's cells

					# print "found previous cell at %s" % str([prev_cell.x, prev_cell.y])

					if len(prev_cell.scouting_numbers) > 1: # cell has been scouted by another
						omit_loc = False # by assumption
						for other in prev_cell.scouting_numbers:
							# if other is scouter: # by this snake: stop

							# 	print "cell already scouted:"

							# 	omit_loc = True
							# 	continue

							len1 = scouter.length()
							len2 = other.length()
							if other in food_eaters:
								len2 += 1

							if len2 >= len1: # by a longer snake: stop
								omit_loc = True
								continue

						if omit_loc:
							scouter.scouted[sd-1].remove(prev_cell)
							continue # for scouter; level 4


					next_moves = self.neighbours_clear_for_scouting(scouter, prev_cell.x, prev_cell.y)

					for move in next_moves:

						# scouting numbers may not even be needed
						move.scouting_numbers[scouter] = sd


						scouter.scouted[sd].append(move)

						move.scouting_precursors[scouter] = [] 
						for nearby in self.board.neighbours(move.x, move.y):
							nearby_cell = self.board.get_cell(*nearby)
							if scouter in nearby_cell.scouting_numbers:
								if nearby_cell.scouting_numbers[scouter] == sd - 1: # like this one
									move.scouting_precursors[scouter].append(nearby_cell)


						if 'food' in move.contains:
							food_eaters.append(scouter)
							if not scouter.scout_tail is None:
								tail_cell.scouting_delay += 1


				if scouter.scouted[sd] != []:
					num_snakes_that_found_new_cells += 1

			if last_turn:
				# can_advance_tails = False
				pass

			if num_snakes_that_found_new_cells == 0:
				break

			sd += 1
		sd -= 1


		# remove unsafe squares
		for scouter in self.snake_list:
			for row in scouter.scouted:
				marked_for_removal = []
				for cell in row:
					if len(cell.scouting_numbers) > 1: # cell has been scouted by another
						for other in cell.scouting_numbers:

							if other is scouter:
								# if scouter is self.player:
								# 	print '%s was me' % other
								continue

							if cell.scouting_numbers[other] > cell.scouting_numbers[scouter]:
								
								# if scouter is self.player:
									# print '%s cant get to %s before %s' % (other, cell, scouter)
								continue

							# print cell.scouting_numbers

							len1 = scouter.length()
							len2 = other.length()
							if other in food_eaters:
								len2 += 1
							if scouter in food_eaters:
								len1 += 1

							if len2 >= len1: # by a mean snake: stop
								# print '%s is scared of %s getting to %s' % (scouter, other, cell)
								marked_for_removal.append(cell)

				for cell in marked_for_removal:
					while cell in row:
						row.remove(cell)



		# trim snake.scouted
		for snake in self.snake_list:
			last_row = None
			for i in range(1, len(snake.scouted)+1):
				if snake.scouted[-i] != []:
					last_row = -i
					break
			if (not last_row is None) and last_row != -1:
				snake.scouted = snake.scouted[0:last_row+1]

		print "Farthest scouted: %d" % sd				
		print "Time taken to scout: %s" % str(time.time() - start_time)
		return True

	

	def starving(self, asker):
		return 1-((asker.health())/100.0)

	def greed_priority(self, asker, cell, max_df, max_ff):
		f = 0
		d = 0

		if max_ff != 0:
			f = cell.scout_favour[asker]['food']/max_ff
		if max_df != 0:
			d = cell.scout_favour[asker]['distance']/max_df

		# g = 0
		# max_snake_length = max(map(lambda s: s.length(), filter(lambda s: not s is self.player,  self.snake_list)))
		# l = self.player.length()
		# g = 1 + max_snake_length*1.4/l

		s = self.starving(asker)

		food_modifier = 1.1*s*s-0.1

		# return f*s*g+(1.0-s)*d**2

		return f*food_modifier+d*d*(1-s)

	def actual_greed(self, asker):
		# subtract 1 because of head cell
		# total_scouted = sum([len(line) for line in self.player.scouted]) - 1
		# total_food = len(self.food_cells)
		# if total_food > 0:
		# 	food_bit = 1.0/total_food
		start_time = time.time()

		me = asker
		health = asker.health()
		length = asker.length()

		distance = 0

		food_good = True
		food_found = False

		for row in me.scouted[::-1][:-1]:
			# if row[0].scouting_numbers[me] == 0:
			# 	break

			if food_found:
				food_good = False

			for cell in row:

				# print "%s precursors:" % str(cell)
				# print [cell.scouting_precursors]
				distance = cell.scouting_numbers[me]

				if me not in cell.scout_favour:
					far_bonus = 0.0
					if row == me.scouted[-1]:
						far_bonus = 1.0
					cell.scout_favour[me] = {}
					cell.scout_favour[me]['distance'] = far_bonus
					cell.scout_favour[me]['food'] = 0.0

				if 'food' in cell.contains:
					# if food_good:
					if True:
						nominal_health = max(0, health - distance)
						food_value = 0.0
						if nominal_health > 0:
							food_value = 10.0/(nominal_health)
							food_found = True
						cell.scout_favour[me]['food'] += food_value
						# print"Ff now %s" % cell.scout_favour[me]['food']
					else:
						cell.scout_favour[me]['food'] /= 2.0
						# print"Ff now %s" % cell.scout_favour[me]['food']

				if me not in cell.scouting_precursors:
					continue

				pres = cell.scouting_precursors[me]
				div = float(len(pres))
				if div > 0:
					for pre in pres:
						if me not in pre.scout_favour:
							pre.scout_favour[me] = {}
							pre.scout_favour[me]['distance'] = 0.0
							pre.scout_favour[me]['food'] = 0.0
						pre.scout_favour[me]['distance'] += cell.scout_favour[me]['distance']/div
						pre.scout_favour[me]['food'] += cell.scout_favour[me]['food']/div

		end_time = time.time()
		print "Greed time: %s" % str(end_time-start_time)

		# now choose best option
		if len(me.scouted) > 1:
			options = me.scouted[1]
		else:
			return 'left'
		
		total_food_favour = sum(cell.scout_favour[me]['food'] for cell in options)
		total_distance_favour = sum(cell.scout_favour[me]['distance'] for cell in options)

		# if len(options) == 0:
		# 	return 'left'

		if len(options) == 1:
			choice = options[0]

		else:
			choice = sorted(options, key= lambda cell: self.greed_priority(me, cell, total_distance_favour, total_food_favour))[-1]

		here = me.bodypart_location(0)
		there = (choice.x, choice.y)
		return directionary[closest_direction(*here+there)]

		return directionary[closest_direction(me.bodypart_location(0)[0], me.bodypart_location(0)[1], self.food_cells[0].x,self.food_cells[0].y)]



	def dfs(self, asker):

		start_time = time.time()
		
		stack = deque()

		asker.dfs_root = cell_node(self.board.get_cell(*asker.bodypart_location(0)))
		
		stack.append(asker.dfs_root)

		while stack:
			cur = stack.pop()
			cur_loc = (cur.cell.x, cur.cell.y)
			neighbours = [self.board.get_cell(*loc) for loc in self.board.neighbours(*cur_loc)]
			neighbours = filter(lambda cell: cell.node is None, neighbours)

			for n in neighbours:
				new_node = cell_node(n)
				cur.add_child(new_node)
				stack.append(new_node)

			if neighbours == []:
				asker.dfs_endpoints.append(cur)

		asker.dfs_root.calculate_distances()
		asker.dfs_root.calculate_sums(self.snake_list)

		end_time = time.time()

		print "DFS time: %s" % str(end_time - start_time)



	def best_endpoint(self):

		endpoints = self.player.dfs_endpoints

		if endpoints == []:
			return None

		food_good = lambda node: (node.sums['foodlist'] != []) and self.player.health() - min(node.sums['foodlist']) > 1
		d_key = lambda node: node.sums['favour']

		endpoints_fg = list(filter(food_good, endpoints))

		if endpoints_fg != []:
			endpoints = endpoints_fg
			
		endpoints = sorted(endpoints, key=d_key)

		if endpoints == []:
			return None

		return endpoints[-1]


	def best_direction(self):

		vec_a = self.player.bodypart_location(0)
		c = self.best_endpoint()
		if c is None:
			return None

		c = c.scouting_intersect(self.player)

		if c is None:
			return None

		c = c.cell.originator(self.player)

		if c is None:
			return None

		
		return directionary[closest_direction(vec_a[0], vec_a[1], c.x, c.y)]


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
					tmp += "[%.2f]" % (cell.scout_favour[snake]['food'])
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
					tmp += "[    ]"
			strings.append(tmp)
		return strings

