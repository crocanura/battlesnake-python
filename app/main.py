import bottle
import os
import random
import pickle



data_dump = None #REMOVE WHEN POSSIBLE
last_move = None #REMOVE WHEN POSSIBLE



def build_board(data):
    board = []
    for i in range(data.get('width')):
        board.append([])
        for j in range(data.get('height')):
            board[i].append({})

    for snake in data['snakes']['data']:
        body = snake['body']['data']
        for i in range(snake['length']):
            point = body[i]
            board[point['x']][point['y']]['snake'] = {snake['name']:i}

    for food in data['food']['data']:
        board[food['x']][food['y']]['food'] = True

    return board



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
        'taunt': 'I am a snek',
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
        # board = build_board(data)
        pass

    data_dump = data



    global last_move
    
    # Naive snake
    options = ['up', 'down', 'left', 'right']
    if last_move in options:
        options.remove(last_move)

    direction = random.choice(options)
    print direction
    return {
        'move': direction,
        'taunt': 'I go!'
    }


# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()

if __name__ == '__main__':
    bottle.run(
        application,
        host=os.getenv('IP', '127.0.0.1'),
        port=os.getenv('PORT', '8080'),
        debug = True)
