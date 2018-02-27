import pickle
import requests

downl = requests.get("https://lwotzke-snake1.herokuapp.com/data")

data = pickle.loads(downl.text)

