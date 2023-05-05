# import the opencv library
from datetime import datetime

import cv2

from raspberryturk.core import mkdir, opencv

IMG_DIR = mkdir("data/raw_new/")

cam = opencv.Camera(port=4, res=(1280, 720))

while (True):
    frame = cam.frame

    # Display the resulting frame
    cv2.imshow('frame', frame)
    cv2.imwrite(str(IMG_DIR / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"), frame)

    # the 'Q' button is set as the
    # quitting button you may use any
    # desired button of your choice
    if cv2.waitKey(1000) & 0xFF == ord('q'):
        break

cam.__exit__()

# After the loop release the cap object
# Destroy all the windows
cv2.destroyAllWindows()
