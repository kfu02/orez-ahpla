import pickle
from game import *

f = open(filepath, 'rb')
game_log = pickle.load(f)
f.close()

for moves in game_log:
    pass
