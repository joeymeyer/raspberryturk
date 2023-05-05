import logging
from time import sleep

import numpy as np

from core import opencv
from raspberryturk import lib_path, RaspberryTurkError, setup_console_logging


def _chessboard_perspective_transform_path():
    return lib_path('chessboard_perspective_transform.npy')


def get_chessboard_perspective_transform():
    try:
        M = np.load(_chessboard_perspective_transform_path())
        return M
    except IOError:
        raise RaspberryTurkError("No chessboard perspective transform found. Camera position recalibration required.")


def recalibrate_camera_position(frame):
    import cv2
    from itertools import product
    from sklearn.linear_model import LinearRegression
    from sklearn.preprocessing import PolynomialFeatures
    from scipy.spatial.distance import euclidean

    board_size = (7, 7)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    cv2.imwrite('frame.png', frame)
    found, corners = cv2.findChessboardCorners(
        frame, board_size,
        flags=cv2.CALIB_CB_NORMALIZE_IMAGE | cv2.CALIB_CB_ADAPTIVE_THRESH,
        # flags=cv2.CALIB_CB_NORMALIZE_IMAGE,
    )

    assert found, "Couldn't find chessboard."

    z = corners.reshape((49, 2))

    board_center = z[24]
    frame_center = frame.shape[1] / 2.0, frame.shape[0] / 2.0

    assert euclidean(board_center, frame_center) < 20.0, "Camera is not centered over chessboard."

    X_train = np.array(list(product(np.linspace(-3, 3, 7), np.linspace(-3, 3, 7))))

    poly = PolynomialFeatures(degree=4)
    X_train = poly.fit_transform(X_train)

    m_x = LinearRegression()
    m_x.fit(X_train, z[:, 0])

    m_y = LinearRegression()
    m_y.fit(X_train, z[:, 1])

    def predict(i, j):
        features = poly.fit_transform(np.array([i, j]))
        return m_x.predict(features), m_y.predict(features)

    P = []
    Q = []

    P.append(predict(-4.0, -4.0))
    Q.append((0.0, 0.0))

    P.append(predict(-4.0, 4.0))
    Q.append((0.0, 480.0))

    P.append(predict(4.0, -4.0))
    Q.append((480.0, 0.0))

    P.append(predict(4.0, 4.0))
    Q.append((480.0, 480.0))

    Q = np.array(Q, np.float32)
    P = np.array(P, np.float32).reshape(Q.shape)
    ind = np.lexsort((P[:,1],P[:,0]))
    P = P[ind]

    M = cv2.getPerspectiveTransform(P, Q)
    np.save(_chessboard_perspective_transform_path(), M)

def main():
    setup_console_logging()
    logger = logging.getLogger(__name__)
    logger.info("Begin camera position recalibration...")
    try:
        with opencv.Camera(4, (1280, 720)) as cam:
            sleep(2)
            recalibrate_camera_position(cam.frame)
    except AssertionError as e:
        logger.error(e)
    else:
        logger.info("Camera position recalibration successful.")


if __name__ == '__main__':
    main()
