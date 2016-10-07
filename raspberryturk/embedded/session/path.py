import os

def session_path(filename=''):
    base_path = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(base_path, '.session', filename)
