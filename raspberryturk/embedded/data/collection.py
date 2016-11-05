import numpy as np
import cv2
import os
import argparse
from time import time
import chess
import random
from raspberryturk.core.vision.constants import SQUARE_SIZE, BOARD_SIZE
from raspberryturk.embedded.vision.chess_camera import ChessCamera

class RandomBoard():
    def __init__(self, num_white_pawns=8, num_white_knights=2, num_white_bishops=2,
                 num_white_rooks=2, num_white_queens=2, num_white_kings=1,
                 num_black_pawns=8, num_black_knights=2, num_black_bishops=2,
                 num_black_rooks=2, num_black_queens=2, num_black_kings=1, seed=1):
        self.rotation = 0
        self.seed = seed
        random.seed(seed)
        self.pieces = []
        self.pieces += [chess.Piece(chess.PAWN, chess.WHITE)]    * num_white_pawns
        self.pieces += [chess.Piece(chess.KNIGHT, chess.WHITE)]  * num_white_knights
        self.pieces += [chess.Piece(chess.BISHOP, chess.WHITE)]  * num_white_bishops
        self.pieces += [chess.Piece(chess.ROOK, chess.WHITE)]    * num_white_rooks
        self.pieces += [chess.Piece(chess.QUEEN, chess.WHITE)]   * num_white_queens
        self.pieces += [chess.Piece(chess.KING, chess.WHITE)]    * num_white_kings
        self.pieces += [chess.Piece(chess.PAWN, chess.BLACK)]    * num_black_pawns
        self.pieces += [chess.Piece(chess.KNIGHT, chess.BLACK)]  * num_black_knights
        self.pieces += [chess.Piece(chess.BISHOP, chess.BLACK)]  * num_black_bishops
        self.pieces += [chess.Piece(chess.ROOK, chess.BLACK)]    * num_black_rooks
        self.pieces += [chess.Piece(chess.QUEEN, chess.BLACK)]   * num_black_queens
        self.pieces += [chess.Piece(chess.KING, chess.BLACK)]    * num_black_kings
        self.pieces += [None] * (64 - len(self.pieces))
        random.shuffle(self.pieces)

    def chessboard(self):
        board = chess.BaseBoard.empty()
        for i in range(64):
            board.set_piece_at(i, self.pieces[i])
        return board

    def __str__(self):
        return str(self.chessboard())

    def fen(self):
        return self.chessboard().board_fen()

    def increment(self):
        self.rotation = self.rotation + 1
        self.pieces.insert(0, self.pieces.pop())

def _seed_path(base_path, random_board, filename):
    path_items = [base_path, str(random_board.seed), str(random_board.rotation)]
    if filename is not None:
        path_items.append(filename)
    return os.path.join(*path_items)

def _create_collection_folder(base_path, random_board):
    if not os.path.exists(_seed_path(base_path, random_board, None)):
        os.makedirs(_seed_path(base_path, random_board, None))
    fen_file = _seed_path(base_path, random_board, "board.fen")
    if not os.path.exists(fen_file):
        with open(fen_file, 'w') as f:
            f.write(random_board.fen())

def _capture_chessboard(base_path, random_board, frame):
    path = _seed_path(base_path, random_board, str(int(time())) + ".jpg")
    cv2.imwrite(path, frame)

def _get_args():
    desc = "Utility used to capture chessboard images and associated FENs. \
    While the script is running use 'r' to rotate the pieces on the board, 'c' \
    to capture the current frame, and 'q' to quit."
    prog = os.path.relpath(__file__)
    parser = argparse.ArgumentParser(prog=prog, description=desc)
    parser.add_argument('base_path', type=os.path.abspath,
                        help="Base path for data collection.")
    parser.add_argument('-s', '--seed', default=1, type=int,
                        help="Random seed to initialize board.")
    return parser.parse_args()

def main():
    args = _get_args()
    rb = RandomBoard(seed=args.seed)
    _create_collection_folder(args.base_path, rb)
    end = False

    cam = ChessCamera()

    while not end:
        cbf = cam.current_chessboard_frame()
        img = cbf.img.copy()

        for i in range(1, 8):
            mx_pt = int((i / 8.0) * BOARD_SIZE)
            cv2.line(img, (0, mx_pt), (BOARD_SIZE, mx_pt), (255,255,255))
            cv2.line(img, (mx_pt, 0), (mx_pt, BOARD_SIZE), (255,255,255))

        for i in range(64):
            piece = rb.pieces[i]
            x = (i % 8) * SQUARE_SIZE
            y = BOARD_SIZE - (i / 8) * SQUARE_SIZE - SQUARE_SIZE
            if piece is not None:
                text = str(piece)
                cv2.putText(img, text, (x+10,y+20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1, cv2.LINE_AA)

        cv2.imshow(os.path.relpath(__file__), img)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('r'):
            rb.increment()
            _create_collection_folder(args.base_path, rb)
        elif key == ord('c'):
            _capture_chessboard(args.base_path, rb, cbf.img)
        elif key == ord('q'):
            end = True

    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
