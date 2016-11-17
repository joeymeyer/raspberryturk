import numpy as np
import chess
from copy import copy

def _colored_board_mask_for_board(board):
    colored_board_mask = [None] * 64
    for i in range(64):
        p = board.piece_at(i)
        if p is not None:
            colored_board_mask[i] = p.color
    return colored_board_mask

def possible_moves_for_board(board, colored_board_mask):
    possible_moves = []
    for move in board.legal_moves:
        board_copy = copy(board)
        board_copy.push(move)
        if _colored_board_mask_for_board(board_copy) == colored_board_mask:
            possible_moves.append(move)
    return possible_moves

def pawn_board_from_colored_board_mask(cbm):
    b = chess.BaseBoard.empty()
    for i in range(64):
        c = cbm[i]
        if c is not None:
            b.set_piece_at(i, chess.Piece(chess.PAWN, c))
    return b