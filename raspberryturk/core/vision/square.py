class Square(object):
    def __init__(self, position, raw_img):
        self.position = position
        self.raw_img = raw_img

    def is_grayscale(self):
        return len(self.raw_img.shape) is 2
