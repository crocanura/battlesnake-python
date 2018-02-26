import pickle
import requests

downl = requests.get("https://lwotzke-snake1.herokuapp.com/data")

obj = pickle.loads(downl.text)

