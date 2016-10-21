import numpy as np
import cv2
import os
import argparse
from raspberryturk.core.vision.square import Square
from raspberryturk.external.data import class_encoding
from raspberryturk.external.data.dataset import Dataset
from tqdm import tqdm
from random import shuffle
from class_encoding import ENCODING_FUNCTIONS
from sklearn.model_selection import train_test_split
from raspberryturk.core.data.raw_pixels_extractor import RawPixelsExtractor

def _should_add_square(encoding_function, symbol, rotation, rotation_degree):
    return encoding_function(symbol) >= 0 and (rotation or (rotation_degree is '0'))

def _load_squares(processed_path, grayscale, rotation, encoding_function, sample):
    squares = []
    symbols = []
    imgs_path = os.path.join(processed_path, 'grayscale' if grayscale else 'rgb')
    img_names = os.listdir(imgs_path)
    if sample < 1.0:
        shuffle(img_names)
        sample_index = int(sample*len(img_names))
        img_names = img_names[:sample_index]
    for img_name in tqdm(img_names):
        fn, ext = os.path.splitext(os.path.basename(img_name))
        if ext.lower().endswith(('.png', '.jpg', '.jpeg')):
            symbol, position, rotation_degree, _ = fn.split("-")
            if grayscale:
                symbol = symbol.lower()
            if _should_add_square(encoding_function, symbol, rotation, rotation_degree):
                raw_img = cv2.imread(os.path.join(imgs_path, img_name), 0 if grayscale else 1)
                sq = Square(position, raw_img)
                squares.append(sq)
                symbols.append(symbol)
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
        self.processed_path = os.path.join(base_path, 'processed')
        self.encoding_function = encoding_function
        self.squares, self.symbols  = _load_squares(self.processed_path, grayscale, rotation, encoding_function, sample)

    def create_dataset(self, feature_extractor, one_hot=False, test_size=0.20, equalize_class_distribution=False, zca_whiten=False):
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

        return Dataset(X_train, X_val, y_train, y_val, zca=zca)

class _ClassEncodingAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        value_lookup = {f.func_name:f for f in class_encoding.ENCODING_FUNCTIONS}
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
                        choices=[f.func_name for f in class_encoding.ENCODING_FUNCTIONS],
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


def main():
    args = _get_args()
    dc = DatasetCreator(args.base_path, args.encoding_function, grayscale=args.grayscale, \
                        rotation=args.rotation, sample=args.sample)
    dataset = dc.create_dataset(RawPixelsExtractor(), one_hot=args.one_hot, test_size=args.test_size, \
                      equalize_class_distribution=args.equalize_classes, zca_whiten=args.zca)
    dataset.save_file(args.filename)

if __name__ == '__main__':
    main()
