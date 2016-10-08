import cv2
from raspberryturk.core.vision.chessboard_frame import ChessboardFrame
from raspberryturk.core.vision.constants import BOARD_SIZE, SQUARE_SIZE
from raspberryturk.embedded.session.chessboard_perpective_transform import get_chessboard_perspective_transform

class ChessCamera(object):
    def __init__(self):
        self.capture = cv2.VideoCapture(0)

    def current_chessboard_frame(self):
        _, frame = self.capture.read()
        h, w = frame.shape[:2]
        M = get_chessboard_perspective_transform()
        bgr_img = cv2.warpPerspective(frame, M, (BOARD_SIZE,BOARD_SIZE))
        img = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2RGB)
        return ChessboardFrame(img)
