import RPi.GPIO as GPIO
from time import sleep

electromagnet_pin = 40
servo_pin = 38

class Gripper(object):
    def __init__(self):
        self.previous_z = None
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(servo_pin, GPIO.OUT)
        GPIO.setup(electromagnet_pin, GPIO.OUT)

    def calibrate(self):
        self.move(100)

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

    def pickup(self, z):
        self.move(z)
        sleep(0.4)
        self.electromagnet(True)
        sleep(0.2)
        self.move(100)

    def dropoff(self, z):
        self.move(z)
        sleep(0.2)
        self.electromagnet(False)
        sleep(0.4)
        self.move(100)

    def cleanup(self):
        GPIO.cleanup()
