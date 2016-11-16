import random

class Player(object):
    def __init__(self):
        pass

    def select_move(self, board):
        return random.choice(list(board.legal_moves))
