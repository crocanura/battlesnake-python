import bottle
import os
import random
import pickle



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
        'color': ''.join('%02x%02x%02x' % (random.randint(64,196), 0, random.randint(196, 256))).upper(),
        'taunt': 'I am a snek',
        'head_url': head_url,
        'name': 'battlesnake-python',
        'head_type': 'fang'
    }

pickled_request = False

@bottle.post('/move')
def move():
    data = bottle.request.json

    # TODO: Do things with data

    if pickled_request == False:
    	print("trying to pickle")

    	f = open("pickled_data_object", 'w')
    	pickle.dump(data, f)
    	f.close()
    	pickled_request = True

    	print("tried to pickle")
    
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
