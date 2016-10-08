import time
import serial
import numpy as np

from pypose.ax12 import *
from pypose.driver import Driver

SERVO_1 = 1
SERVO_2 = 2
SERVOS = [SERVO_2, SERVO_1]
MIN_SPEED = 20
MAX_SPEED = 80
RESTING_POSITION = (512, 512)

def _register_bytes_to_value(register_bytes):
    return register_bytes[0] + (register_bytes[1]<<8)

def _adjusted_speed(start_position, goal_position, position, min_speed, max_speed):
    distance = [1.0 - float(abs(position[i]-goal_position[i])) / float(max(abs(start_position[i]-goal_position[i]), 1)) for i in range(len(SERVOS))]
    speed = min_speed + (np.sin(np.pi * np.array(distance)) * (max_speed - min_speed))
    return speed.astype(np.int)

class Arm(object):
    def __init__(self, port="/dev/ttyUSB0"):
        self.driver = Driver(port=port)
        time.sleep(2)

    def close(self):
        self.driver.close()

    def recenter(self):
        self.move((512, 512))

    def return_to_rest(self):
        self.move(RESTING_POSITION)

    def move(self, goal_position):
        start_position = self.current_position()
        self.set_speed([MIN_SPEED, MIN_SPEED])
        for i in SERVOS:
            self.driver.setReg(i, P_GOAL_POSITION_L, [goal_position[i%2]%256, goal_position[i%2]>>8])
        while self._is_moving():
            position = self.current_position()
            speed = _adjusted_speed(start_position, goal_position, position, MIN_SPEED, MAX_SPEED)
            self.set_speed(speed)

    def set_speed(self, speed):
        for i in SERVOS:
            self.driver.setReg(i, P_GOAL_SPEED_L, [speed[i%2]%256, speed[i%2]>>8])

    def current_position(self):
        return self._values_for_register(P_PRESENT_POSITION_L)

    def _is_moving(self):
        return any([self.driver.getReg(index, P_MOVING, 1) == 1 for index in SERVOS])

    def _values_for_register(self, register):
        return [_register_bytes_to_value(self.driver.getReg(index, register, 2)) for index in SERVOS]