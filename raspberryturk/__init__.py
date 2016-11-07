import os
import logging
import time
from socket import gethostname

app_directory = 'raspberryturk'

def _root():
    return os.path.abspath(os.sep)

def _var_subdir(subdir, *paths):
    return os.path.join(_root(), 'var', subdir, app_directory, *paths)

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
    return gethostname() == 'raspberryturk'

LOGGING_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

def setup_console_logging(level=logging.INFO):
    logging.basicConfig(format=LOGGING_FORMAT, level=level)

def setup_file_logging(level=logging.DEBUG):
    timestamp = str(int(time.time()))
    fn = os.extsep.join(["raspberryturk-{}".format(timestamp), 'log'])
    path = log_path(fn)
    logging.basicConfig(format=LOGGING_FORMAT, level=level, filename=path, filemode='w')

def active_log_stream():
    try:
        h = logging.root.handlers[0]
        return h.stream
    except IndexError:
        raise RaspberryTurkError("Logging not setup.")

def active_log_path():
    return active_log_stream().name
