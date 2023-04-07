from pathlib import Path


def mkdir(dir_):
    dir_ = Path(dir_)
    dir_.mkdir(parents=True, exist_ok=True)
    return dir_