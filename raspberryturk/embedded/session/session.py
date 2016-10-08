import os
import numpy as np
import logging

class Session(object):
    def __init__(self):
        self._chessboard_perspective_transform = None

    def _path(self, filename=''):
        return os.path.join(os.path.dirname(os.path.realpath(__file__)), '.session', filename)

    def _chessboard_prespective_transform_path(self):
        return self._path('chessboard_perspective_transform.npy')

    def get_chessboard_perspective_transform(self):
        if self._chessboard_perspective_transform is not None:
            return self._chessboard_perspective_transform
        else:
            try:
                self._chessboard_perspective_transform = np.load(self._chessboard_prespective_transform_path())
                return self._chessboard_perspective_transform
            except IOError:
                logging.error("No chessboard perspective transform found. Camera position recalibration required.")
                return None

    def set_chessboard_perspective_transform(self, chessboard_perspective_transform):
        self._chessboard_perspective_transform = chessboard_perspective_transform
        np.save(self._chessboard_prespective_transform_path(), self._chessboard_perspective_transform)
