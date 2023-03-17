import numpy as np

class Dataset(object):
    def __init__(self, X_train, X_val, y_train, y_val, zca=None, metadata=""):
        self.X_train = X_train
        self.X_val = X_val
        self.y_train = y_train
        self.y_val = y_val
        self.zca = zca
        self.metadata = metadata

    def save_file(self, filename):
        np.savez(filename,
                 X_train=self.X_train,
                 X_val=self.X_val,
                 y_train=self.y_train,
                 y_val=self.y_val,
                 zca=self.zca,
                 metadata=self.metadata,
                 )

    @classmethod
    def load_file(cls, filename):
        data = np.load(filename)
        X_train = data['X_train']
        X_val = data['X_val']
        y_train = data['y_train']
        y_val = data['y_val']

        zca = None
        try:
            zca = data['zca']
        except (KeyError, ValueError):
            pass

        metadata = None
        try:
            metadata = data['metadata']
        except KeyError:
            pass
        return cls(X_train, X_val, y_train, y_val, zca=zca, metadata=metadata)
