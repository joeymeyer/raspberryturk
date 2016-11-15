import numpy as np

class Dataset(object):
    def __init__(self, X_train, X_val, y_train, y_val, zca=None):
        self.X_train = X_train
        self.X_val = X_val
        self.y_train = y_train
        self.y_val = y_val
        self.zca = zca

    def save_file(self, filename):
        with open(filename, 'w') as f:
            np.savez(f, X_train=self.X_train,
                        X_val=self.X_val,
                        y_train=self.y_train,
                        y_val=self.y_val,
                        zca=self.zca)

    @classmethod
    def load_file(cls, filename):
        with open(filename, 'r') as f:
            data = np.load(f)
            X_train = data['X_train']
            X_val = data['X_val']
            y_train = data['y_train']
            y_val = data['y_val']
            zca = None
            try:
                zca = data['zca']
            except KeyError:
                pass
            return cls(X_train, X_val, y_train, y_val, zca=zca)
