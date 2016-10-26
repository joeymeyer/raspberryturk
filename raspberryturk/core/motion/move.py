import numpy as np
import os
import platform
import pickle
from sklearn.neighbors import KDTree
from itertools import product

fn = "move.{0}.kdtree".format(platform.machine())
path = os.path.join(os.path.dirname(__file__), fn)
with open(path, 'rb') as f:
    tree = pickle.load(f)

srange = np.array(list(product(range(1024), range(1024))))

def _kdtree_lookup(pt):
    pt = np.array(pt).reshape(1, -1)
    return srange[tree.query(pt, return_distance=False)[0]][0]

class Move(object):
    def __init__(self, origin, destination, piece_height):
        self.origin = origin
        self.destination = destination
        self.piece_height = piece_height

    def origin_servos(self):
        return _kdtree_lookup(self.origin)

    def destination_servos(self):
        return _kdtree_lookup(self.destination)
