import numpy as np
import pickle
import logging
import chess
from raspberryturk import RaspberryTurkError, opt_path
from raspberryturk.core.data.raw_pixels_extractor import RawPixelsExtractor
from raspberryturk.core.data.class_encoding import empty_or_not

def _convert_to_32bit_pca(pca):
    pca.components_ = pca.components_.astype(np.float32)
    pca.explained_variance_ = pca.explained_variance_.astype(np.float32)
    pca.explained_variance_ratio_ = pca.explained_variance_ratio_.astype(np.float32)
    pca.mean_ = pca.mean_.astype(np.float32)
    pca.noise_variance_ = pca.noise_variance_.astype(np.float32)

def _load_svc(logger):
    try:
        svc_path = opt_path('square_color_detector.svc')
        logger.info("Loading {}...".format(svc_path))
        with open(svc_path, 'rb') as f:
            svc = pickle.load(f)
        pca_path = opt_path('square_color_detector.pca')
        logger.info("Loading {}...".format(pca_path))
        with open(pca_path, 'rb') as f:
            pca = pickle.load(f)
        _convert_to_32bit_pca(pca)
        return svc, pca
    except IOError as e:
        raise RaspberryTurkError("Square color detector can't find required file: {}".format(e.filename))

def _not_empty_class():
    p = chess.Piece(chess.PAWN, chess.WHITE)
    return empty_or_not(p.symbol())

class SquareColorDetector(object):
    def __init__(self):
        logger = logging.getLogger(__name__)
        self._rpe = RawPixelsExtractor()
        self._svc, self._pca = _load_svc(logger)

    def detect(self, square):
        X = self._rpe.extract_features(square).reshape(1,-1).astype(np.float32)
        X_pca = self._pca.transform(X)
        p = self._svc.predict(X_pca)[0]
        if p == 1:
            return chess.BLACK
        elif p == 2:
            return chess.WHITE
        else:
            return None
