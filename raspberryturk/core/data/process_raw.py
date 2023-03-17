import numpy as np
import cv2
import os
import errno
import shutil
import chess
import hashlib
import argparse
from random import random
from raspberryturk import setup_console_logging
from raspberryturk.core.vision.chessboard_frame import ChessboardFrame
from raspberryturk.core.vision.constants import SQUARE_SIZE, BOARD_SIZE

def _create_processed_dir(target_path):
    for sub in ['rgb', 'grayscale']:
        path = os.path.join(target_path, sub)
        try:
            os.makedirs(path)
        except OSError as exception:
            if exception.errno != errno.EEXIST or not os.path.isdir(path):
                raise

def _subdirectories(path):
    return [os.path.join(path,o) for o in os.listdir(path) if os.path.isdir(os.path.join(path,o))
                                                              and not o.startswith('.')]

def _images(path, cache):
    images = []
    for o in os.listdir(path):
        fn, ext = os.path.splitext(os.path.basename(o))
        if o.lower().endswith(('.png', '.jpg', '.jpeg')) and not cache.get(fn, False):
            images.append(os.path.join(path,o))
            cache[fn] = True
    return images

def _rotate(img, angle):
    rows,cols = img.shape[:2]
    M = cv2.getRotationMatrix2D((cols/2,rows/2),angle,1)
    return cv2.warpAffine(img,M,(cols,rows))

def _save_image(fn, img):
    try:
        os.makedirs(os.path.dirname(fn))
    except OSError as e:
        if e.errno != 17:
            raise e
    cv2.imwrite(fn, img)

def _process(board, img, target_path):
    cf = ChessboardFrame(img)
    for i in range(64):
        piece = board.piece_at(i)
        fn = chess.SQUARE_NAMES[i]
        sq = cf.square_at(i)
        rand_addition = hashlib.sha1(str(random()).encode()).hexdigest()[0:24]
        for a in range(0, 360, 90):
            sym = piece.symbol() if piece is not None else 'e'
            img_name = os.extsep.join([rand_addition, 'jpg'])
            rgb_path = os.path.join(target_path, 'rgb', sym, fn, str(a), img_name)
            _save_image(rgb_path, _rotate(sq.raw_img, a))
            grayscale_path = os.path.join(target_path, 'grayscale', sym, fn, str(a), img_name)
            _save_image(grayscale_path, _rotate(cv2.cvtColor(sq.raw_img, cv2.COLOR_BGR2GRAY), a))

def _get_args():
        prog = os.path.relpath(__file__)
        desc = "Utility used to process raw chessboard image data collected by collection.py. \
                It goes through the contents of SOURCE_PATH, processes the collected \
                data, and stores the interim format in TARGET_PATH. By default \
                it will keep track of what raw data has been processed so it can be \
                run multiple times without reprocessing the same data."
        parser = argparse.ArgumentParser(prog=prog, description=desc)
        parser.add_argument('source_path', type=os.path.abspath,
                            help="Source path for data processing.")
        parser.add_argument('target_path', type=os.path.abspath,
                            help="Target path for data processing.")
        parser.add_argument('-x', '--ignore_cache', action='store_true', \
                            help="If True, this will delete all contents \
                                  in the target_path and reprocess everything.")
        return parser.parse_args()

def main():
    args = _get_args()
    setup_console_logging()
    target_path = args.target_path
    if args.ignore_cache:
        shutil.rmtree(target_path)
    _create_processed_dir(target_path)
    cache = {}
    cache_path = os.path.join(target_path, '.squares_cache')
    if not args.ignore_cache:
        try:
            cache = {k:True for k in [line.strip() for line in open(cache_path)]}
        except IOError:
            pass
    source_path = args.source_path
    seed_dirs = _subdirectories(source_path)
    for seed_dir in seed_dirs:
        rotation_dirs = _subdirectories(seed_dir)
        for rotation_dir in rotation_dirs:
            with open(os.path.join(rotation_dir, "board.fen")) as f:
                fen = f.read()
                board = chess.BaseBoard(board_fen=fen)
                for img_path in _images(rotation_dir, cache):
                    img = cv2.imread(img_path)
                    _process(board, img, target_path)
    with open(cache_path, 'w') as f:
        f.write("\n".join(cache.keys()))

if __name__ == '__main__':
    main()
