import cv2
import numpy as np
from itertools import product
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from scipy.spatial.distance import euclidean
from raspberryturk.embedded.session.path import session_path

if __name__ != '__main__':
    exit(0)

board_size = (7,7)
_, frame = cv2.VideoCapture(0).read()
gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
found, corners = cv2.findChessboardCorners(gray, board_size, flags=cv2.CALIB_CB_NORMALIZE_IMAGE|cv2.CALIB_CB_ADAPTIVE_THRESH)

assert found, "Couldn't find chessboard."

z = corners.reshape((49,2))

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

P = np.array(P, np.float32)
Q = np.array(Q, np.float32)

M = cv2.getPerspectiveTransform(P, Q)
np.save(session_path('chessboard_perspective_transform.npy'), M)
print "Camera position recalibration successful."
