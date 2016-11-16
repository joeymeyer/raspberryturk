import numpy as np
from square import Square
from constants import SQUARE_SIZE, BOARD_SIZE

class ChessboardFrame():
    def __init__(self, img):
        self.img = img

    def square_at(self, i):
        x = ((i / 8) % 8) * SQUARE_SIZE
        y = (i % 8) * SQUARE_SIZE
        return Square(i, self.img[x:x+SQUARE_SIZE, y:y+SQUARE_SIZE, :])
