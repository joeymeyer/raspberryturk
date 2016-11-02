import os
import sys
root = os.path.abspath(os.pardir)
if root not in sys.path:
    sys.path.append(root)

def path(*paths):
    return os.path.join(root, *paths)
