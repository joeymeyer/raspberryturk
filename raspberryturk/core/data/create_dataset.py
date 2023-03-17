import numpy as np
import cv2
import os
import argparse
import json
from raspberryturk import setup_console_logging
from raspberryturk.core.vision.square import Square
from raspberryturk.core.data import class_encoding
from raspberryturk.core.data.dataset import Dataset
from random import shuffle
from sklearn.model_selection import train_test_split
from raspberryturk.core.data.raw_pixels_extractor import RawPixelsExtractor

def _should_add_square(encoding_function, symbol, rotation, rotation_degree):
    return encoding_function(symbol) >= 0 and (rotation or (rotation_degree is '0'))

def _load_squares(base_path, grayscale, rotation, encoding_function, sample):
    square_files = []
    path = os.path.join(base_path, 'grayscale' if grayscale else 'rgb')
    for root, dirs, files in os.walk(path):
        subpath = root[len(path):]
        components = subpath.split(os.sep)
        if len(components) == 4:
            _, sym, position, angle = components
            for fn in files:
                _, ext = os.path.splitext(os.path.basename(fn))
                if ext.lower().endswith(('.png', '.jpg', '.jpeg')):
                    sq_path = os.path.join(root, fn)
                    square_files.append((sq_path, sym, position, angle))
    if sample < 1.0:
        shuffle(square_files)
        sample_index = int(sample*len(square_files))
        square_files = square_files[:sample_index]

    squares = []
    symbols = []
    for fn, sym, position, angle in square_files:
        if grayscale:
            sym = sym.lower()
        if _should_add_square(encoding_function, sym, rotation, angle):
            raw_img = cv2.imread(fn, 0 if grayscale else 1)
            sq = Square(position, raw_img)
            squares.append(sq)
            symbols.append(sym)
    return squares, symbols

def _create_features(squares, feature_extractor):
    return np.array([feature_extractor.extract_features(sq) for sq in squares])

def _create_labels(encoding_function, symbols, one_hot):
    labels = np.array([encoding_function(symbol) for symbol in symbols]).astype(np.uint8)
    if one_hot:
        num_labels = labels.shape[0]
        num_classes = encoding_function.num_classes
        index_offset = np.arange(num_labels) * num_classes
        labels_one_hot = np.zeros((num_labels, num_classes), dtype=np.uint8)
        labels_one_hot.flat[index_offset + labels.ravel().astype(np.uint8)] = 1
        labels = labels_one_hot
    return labels

class DatasetCreator(object):
    def __init__(self, base_path, encoding_function, grayscale=True, rotation=False, sample=1.0):
        self.base_path = base_path
        self.encoding_function = encoding_function
        self.squares, self.symbols  = _load_squares(self.base_path, grayscale, rotation, encoding_function, sample)

    def create_dataset(self, feature_extractor, one_hot=False, test_size=0.20, equalize_class_distribution=False, zca_whiten=False, metadata=""):
        features = _create_features(self.squares, feature_extractor)
        labels = _create_labels(self.encoding_function, self.symbols, one_hot=one_hot)

        if equalize_class_distribution:
            equalized_features = []
            equalized_labels = []
            u, cnt = np.unique(labels, return_counts=True)
            min_count = np.min(cnt)
            for c in u:
                ind = (labels == c)
                equalized_features += list(features[ind][:min_count])
                equalized_labels += list(labels[ind][:min_count])
            p = np.random.permutation(len(equalized_labels))
            features = np.array(equalized_features)[p]
            labels = np.array(equalized_labels)[p]

        X_train, X_val, y_train, y_val = train_test_split(features, labels, test_size=test_size)
        zca = None

        if zca_whiten:
            eig_values, eig_vec = np.linalg.eig(np.cov(X_train.T))
            zca = eig_vec.dot(np.diag((eig_values+0.01)**-0.5).dot(eig_vec.T))
            X_train = np.dot(X_train, zca)
            X_val = np.dot(X_val, zca)

        return Dataset(X_train, X_val, y_train, y_val, zca=zca, metadata=metadata)

class _ClassEncodingAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        value_lookup = {f.__name__: f for f in class_encoding.ENCODING_FUNCTIONS}
        setattr(namespace, self.dest, value_lookup[values])

def _bounded_float(x):
    x = float(x)
    if x < 0.0 or x >= 1.0:
        raise argparse.ArgumentTypeError("{0} not in range [0.0, 1.0]".format(x))
    return x

def _get_args():
    prog = os.path.relpath(__file__)
    desc = "Utility used to create a dataset from processed images."
    parser = argparse.ArgumentParser(prog=prog, description=desc)
    parser.add_argument('base_path', type=os.path.abspath,
                        help="Base path for data processing.")
    parser.add_argument('encoding_function', type=str, \
                        choices=[f.__name__ for f in class_encoding.ENCODING_FUNCTIONS],
                        action=_ClassEncodingAction,
                        help="Encoding function to use for piece classification. \
                              See class_encoding.py for possible values.")
    parser.add_argument('filename', type=os.path.abspath,
                        help="Output filename for dataset. Should be .npz")
    parser.add_argument('-g', '--grayscale', action='store_true', \
                        help="Dataset should use grayscale images.")
    parser.add_argument('-r', '--rotation', action='store_true', \
                        help="Dataset should use rotated images.")
    parser.add_argument('-s', '--sample', type=_bounded_float, default=1.0, \
                        help="Dataset should be created by only a \
                              sample of images. Must be value between 0 and 1.")
    parser.add_argument('-o', '--one_hot', action='store_true', \
                        help="Dataset should use one hot encoding for labels.")
    parser.add_argument('-t', '--test_size', type=_bounded_float, default=0.2, \
                        help="Test set partition size. Must be value between 0 and 1.")
    parser.add_argument('-e', '--equalize_classes', action='store_true', \
                        help="Equalize class distributions.")
    parser.add_argument('-z', '--zca', action='store_true', \
                        help="ZCA whiten dataset.")
    return parser.parse_args()

def _json_args(args):
    dict_args = {k: v.__name__ if callable(v) else v for k,v in vars(args).items()}
    return json.dumps(dict_args, indent=2, sort_keys=True)

def main():
    args = _get_args()
    setup_console_logging()
    dc = DatasetCreator(args.base_path, args.encoding_function, grayscale=args.grayscale, \
                        rotation=args.rotation, sample=args.sample)
    dataset = dc.create_dataset(RawPixelsExtractor(), one_hot=args.one_hot, test_size=args.test_size, \
                      equalize_class_distribution=args.equalize_classes, zca_whiten=args.zca, metadata=_json_args(args))
    dataset.save_file(args.filename)

if __name__ == '__main__':
    main()
