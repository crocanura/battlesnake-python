import bottle
import os
import random
import pickle



last_data_obj = None


@bottle.route('/data')
def static():
	return (pickle.dumps(last_data_obj))


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

    ## For development
    global last_data_obj
    last_data_obj = None

    # TODO: Do things with data

    return {
        'color': ''.join('#%02x%02x%02x' % (random.randint(64,196), 0, random.randint(196, 256))).upper(),
        'taunt': 'I am a snek',
        'head_url': head_url,
        'name': 'battlesnake-python',
        'head_type': 'fang'
    }


@bottle.post('/move')
def move():
    data = bottle.request.json

    global last_data_obj

    if last_data_obj == None:
    	last_data_obj = data
    
    directions = ['up', 'down', 'left', 'right']
    direction = random.choice(directions)
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
