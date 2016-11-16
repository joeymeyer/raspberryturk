import cv2
import chess
from raspberryturk.core.vision.chessboard_frame import ChessboardFrame
from raspberryturk.core.vision.constants import BOARD_SIZE, SQUARE_SIZE
from raspberryturk.embedded.vision.chessboard_perspective_transform import get_chessboard_perspective_transform
from raspberryturk.embedded.vision.square_presence_detector import SquarePresenceDetector

class ChessCamera(object):
    def __init__(self):
        self._capture = cv2.VideoCapture(0)
        self._piece_detector = SquarePresenceDetector()

    def current_chessboard_frame(self):
        _, frame = self._capture.read()
        h, w = frame.shape[:2]
        M = get_chessboard_perspective_transform()
        bgr_img = cv2.warpPerspective(frame, M, (BOARD_SIZE,BOARD_SIZE))
        img = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2RGB)
        flipped_img = cv2.flip(img, -1)
        return ChessboardFrame(flipped_img)

    def current_square_set(self):
        cbf = self.current_chessboard_frame()
        ss = chess.SquareSet()
        for i in range(64):
            sq = cbf.square_at(i)
            if self._piece_detector.detect(sq):
                ss.update(chess.SquareSet.from_square(i))
        return ss
