import cv2
import numpy as np

from raspberryturk import RepeatTimer


class Camera:

    def __init__(self,
                 port=0,
                 res=(640, 480),
                 ) -> None:
        self._port = port
        self._frame = np.ndarray(())

        self._vid = cv2.VideoCapture(self._port)
        self._vid.set(cv2.CAP_PROP_FRAME_WIDTH, res[0])
        self._vid.set(cv2.CAP_PROP_FRAME_HEIGHT, res[1])
        # # calibrate
        # for i in range(60):
        #     self._vid.read()
        self._set_img()

        self._timer = RepeatTimer(0.1, self._set_img)
        self._timer.start()

    def __enter__(self):
        return self

    def _set_img(self):
        _, frame = self._vid.read()
        self._frame = frame

    @property
    def frame(self):
        return self._frame

    def __exit__(self):
        self._timer.cancel()
        self._vid.release()
