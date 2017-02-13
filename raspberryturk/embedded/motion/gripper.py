import RPi.GPIO as GPIO
from time import sleep
import chess

electromagnet_pin = 40
servo_pin = 38

PIECE_HEIGHTS = {
    chess.KING: 41,
    chess.QUEEN: 34,
    chess.ROOK: 20,
    chess.BISHOP: 28,
    chess.KNIGHT: 24,
    chess.PAWN: 19
}

MAX_PIECE_HEIGHT = max(PIECE_HEIGHTS.values())
RESTING_HEIGHT = MAX_PIECE_HEIGHT + 15

class Gripper(object):
    def __init__(self):
        self.previous_z = None
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(servo_pin, GPIO.OUT)
        GPIO.setup(electromagnet_pin, GPIO.OUT)

    def calibrate(self):
        self.move(RESTING_HEIGHT)

    def move(self, z):
        z = max(0.0, min(z, 100.0))
        dc = (z * 0.067) + 4.0
        p = GPIO.PWM(servo_pin, 50.0)
        p.start(dc)
        if self.previous_z is None:
            t = 10.0
        else:
            t = (abs(self.previous_z - z) / 10.0) + 0.5
        sleep(t)
        p.stop()
        del p
        self.previous_z = z

    def electromagnet(self, on):
        output = GPIO.HIGH if on else GPIO.LOW
        GPIO.output(electromagnet_pin, output)

    def pickup(self, piece_type):
        piece_height = PIECE_HEIGHTS[piece_type]
        self.move(piece_height)
        sleep(0.4)
        self.electromagnet(True)
        sleep(0.2)
        self.move(RESTING_HEIGHT + piece_height)

    def dropoff(self, piece_type):
        piece_height = PIECE_HEIGHTS[piece_type]
        self.move(piece_height)
        sleep(0.2)
        self.electromagnet(False)
        sleep(0.4)
        self.move(RESTING_HEIGHT)

    def cleanup(self):
        GPIO.cleanup()
