import os
from logging.config import fileConfig
from socket import gethostname
base_path = os.path.dirname(os.path.realpath(__file__))
fileConfig(os.path.join(base_path, 'logging.ini'))

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

class RaspberryTurkError(Exception):
    pass

def is_running_on_raspberryturk():
    return gethostname() == 'raspberryturk'

if is_running_on_raspberryturk():
    def _safe_makedirs(path):
        try:
            os.makedirs(path)
        except OSError as e:
            if e.errno != 17:
                raise e
    dirs = [cache_path(), lib_path(), games_path(), opt_path()]
    [_safe_makedirs(d) for d in dirs]
