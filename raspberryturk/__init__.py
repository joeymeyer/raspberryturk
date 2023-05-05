import os
import logging
from logging.handlers import RotatingFileHandler
import time
from socket import gethostname

__author__ = 'Joey Meyer'
__email__ = 'jmeyer41@gmail.com'
__version__ = '0.0.1-beta'

from threading import Timer

app_directory = 'raspberryturk'

def _root():
    return os.path.abspath(os.sep)

def _var_subdir(subdir, *paths):
    return os.path.join('var', subdir, app_directory, *paths)

def cache_path(*paths):
    return _var_subdir('cache', *paths)

def lib_path(*paths):
    return _var_subdir('lib', *paths)

def games_path(*paths):
    return _var_subdir('games', *paths)

def opt_path(*paths):
    return _var_subdir('opt', *paths)

def run_path(*paths):
    return _var_subdir('run', *paths)

def log_path(*paths):
    return _var_subdir('log', *paths)

class RaspberryTurkError(Exception):
    pass

def is_running_on_raspberryturk():
    # return gethostname() == 'raspberryturk'
    return True

LOGGING_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

def setup_console_logging(level=logging.INFO):
    logging.basicConfig(format=LOGGING_FORMAT, level=level)

def setup_file_logging(level=logging.DEBUG):
    path = log_path(os.extsep.join(['raspberryturk', 'log']))
    handler = RotatingFileHandler(path, mode='a', maxBytes=64*1024*1024,
                                  backupCount=5, encoding=None, delay=0)
    handler.setFormatter(logging.Formatter(LOGGING_FORMAT))
    handler.setLevel(level)
    logging.root.setLevel(level)
    logging.root.addHandler(handler)

def active_log_stream():
    try:
        h = logging.root.handlers[0]
        return h.stream
    except IndexError:
        raise RaspberryTurkError("Logging not setup.")

def active_log_path():
    return active_log_stream().name


class RepeatTimer(Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)
