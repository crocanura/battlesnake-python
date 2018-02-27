import bottle
import os
import math

import pickle
import random


#GLOBALS
data_dump = None #REMOVE WHEN POSSIBLE
last_move = None #REMOVE WHEN POSSIBLE
tauntstr = 'I am snek'


def build_board(data):
    board = []
    for i in range(data.get('height')):
        board.append([])
        for j in range(data.get('width')):
            board[i].append({})

    for snake in data['snakes']['data']:
        body = snake['body']['data']
        for i in range(snake['length']):
            point = body[i]
            board[point['y']][point['x']]['snake'] = {snake['name']:i}

    for food in data['food']['data']:
        board[food['y']][food['x']]['food'] = True

    return board


# boolean that tell you if such a key is in one of the cell dictionaries
def among(x, cells):
    for cell in cells:
        if x in cell:
            return True
    return False


# returns a list of x,y tuples of the neighbors to a cell
def neighbours(here, width, height):

    x, y = here

    vals = []
    if x + 1 < width:
        vals.append(tuple([here[0]+1, here[1]]))
    if x - 1 >= 0:
        vals.append(tuple([here[0]-1, here[1]]))
    if y - 1 >= 0:
        vals.append(tuple([here[0], here[1]-1]))
    if y + 1 < height:
        vals.append(tuple([here[0], here[1]+1]))

    return vals


directions = ['left', 'right', 'up', 'down']

# if this is x2 - x1, is x2 on the right or the left?
def leftright(x):
    if x >= 0:
        return 'right'
    return 'left'

# if this is x2 - x1, is x2 on the top or the bottom?
def updown(y):
    if y >= 0:
        return 'down'
    return 'up'

# like a function of type f(direction, tup) but marginally faster
grid_loc_in_dir = {}
grid_loc_in_dir['right'] = lambda tup: (tup[0]+1, tup[1])
grid_loc_in_dir['left'] = lambda tup: (tup[0]-1, tup[1])
grid_loc_in_dir['up'] = lambda tup: (tup[0], tup[1]-1)
grid_loc_in_dir['down'] = lambda tup: (tup[0], tup[1]+1)

# taxicab distance function
taxicab = lambda here, there: abs(here[0]-there[0]) + abs(here[1]-there[1])



def myopic_move(data, board):
    global tauntstr
    tauntstr = 'Food!'

    head = data['you']['body']['data'][0]
    here = (head['x'], head['y'])
    width = data.get('width')
    height = data.get('height')

    open_squares = neighbours(here, width, height)
    open_squares = filter(lambda tup: 'snake' not in board[tup[1]][tup[0]], open_squares)
    for square in open_squares:
        # if among('snake', [board[t[1]][t[0]] for t in neighbours(square, width, height)]):
        for cell in [board[t[1]][t[0]] for t in neighbours(square, width, height)]:
            if 'snake' in cell:
                for name in cell['snake']:
                    if cell['snake'][name] == 0:
                        if not (cell['x'] == data['you']['body']['data'][0]['x']):
                            if not (cell['x'] == data['you']['body']['data'][0]['x']):
                                open_squares.remove(square)
                                tauntstr = '%sH'%(''.join('A' for i in range(random.randint(2,10))))
                                tauntstr += ''.join('!' for i in range(random.randint(1,4)))
                                print tauntstr
                                

    foods = sorted(data['food']['data'], key = lambda food: math.ceil(taxicab(here, (food['x'],food['y']))))

    target = (foods[0]['x'], foods[0]['y'])

    vec = (target[0] - here[0], target[1] - here[1])

    preferences = []
    if abs(vec[0]) >= abs(vec[1]):
        preferences.append(leftright(vec[0]))
        preferences.append(updown(vec[1]))
        if 'up' in preferences:
            preferences.append('down')
        else:
            preferences.append('up')
        if 'right' in preferences:
            preferences.append('left')
        else:
            preferences.append('right')
    else:
        preferences.append(updown(vec[1]))
        preferences.append(leftright(vec[0]))
        if 'right' in preferences:
            preferences.append('left')
        else:
            preferences.append('right')
        if 'up' in preferences:
            preferences.append('down')
        else:
            preferences.append('up')

    for direction in preferences:
        hope = grid_loc_in_dir[direction](here)
        if hope in open_squares:
            return direction

    return 'up'
        


    # neighbour_cells = map(lambda tup: board[tup[1]][tup[0]], neighbours(here, width, height))
    # destinations = filter(lambda cell: 'snake' not in cell, neighbour_cells)



@bottle.route('/data')
def static():
    return (pickle.dumps(data_dump))


@bottle.route('/')
def static():
    return "the server is running"


@bottle.route('/static/<path:path>')
def static(path):
    return bottle.static_file(path, root='static/')


@bottle.post('/start')
def start():
    data = bottle.request.json
    game_id = data.get('game_id')
    board_width = data.get('width')
    board_height = data.get('height')


    head_url = '%s://%s/static/head.png' % (
        bottle.request.urlparts.scheme,
        bottle.request.urlparts.netloc
    )

    # TODO: Do things with data

    return {
        'color': ''.join('#%02x%02x%02x' % (255, random.randint(30,80), 0)).upper(),
        'taunt': tauntstr,
        'head_url': head_url,
        'name': 'battlesnake-python',
        'head_type': 'fang'
    }


@bottle.post('/move')
def move():
    data = bottle.request.json

    ## For development
    global data_dump


    # game board
    board = None
    if data != None:
        board = build_board(data)
        # pass

    data_dump = [data, board]


    direction = myopic_move(data, board)

    # global last_move
    
    # Naive snake
    # options = ['up', 'down', 'left', 'right']
    # if last_move in options:
    #     options.remove(last_move)

    # direction = random.choice(options)


    print direction
    return {
        'move': direction,
        'taunt': tauntstr
    }


# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()

if __name__ == '__main__':
    bottle.run(
        application,
        host=os.getenv('IP', '127.0.0.1'),
        port=os.getenv('PORT', '8080'),
        debug = True)
