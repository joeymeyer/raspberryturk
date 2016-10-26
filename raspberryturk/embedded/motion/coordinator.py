from gripper import Gripper
from arm import Arm

class Coordinator(object):
    def __init__(self):
        self.gripper = Gripper()
        self.arm = Arm()

    def move_piece(self, move):
        self.arm.move(move.origin_servos())
        self.gripper.pickup(move.piece_height)
        self.arm.move(move.destination_servos())
        self.gripper.dropoff(move.piece_height)
        self.arm.return_to_rest()
