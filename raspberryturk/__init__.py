import os
from logging.config import fileConfig
base_path = os.path.dirname(os.path.realpath(__file__))
fileConfig(os.path.join(base_path, 'logging.ini'))
