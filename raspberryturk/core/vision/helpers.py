import numpy as np
import chess
from copy import copy

def _square_set_after_applying_move(board, move):
    board_copy = copy(board)
    board_copy.push(move)
    return _square_set_for_board(board_copy)

def _square_set_for_board(board):
    occupied_squares = [chess.SquareSet.from_square(i) for i in range(64) if board.piece_at(i) is not None]
    mask = np.bitwise_or.reduce(occupied_squares)
    return chess.SquareSet(mask)

def possible_moves_for_board(board, square_set):
    return [move for move in board.legal_moves if _square_set_after_applying_move(board, move).mask == square_set.mask]
