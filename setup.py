#!/usr/bin/env python

from setuptools import setup, find_packages
import raspberryturk

setup(name='raspberryturk',
      version=raspberryturk.__version__,
      description='Python package powering the Raspberry Turk chess-playing robot.',
      author=raspberryturk.__author__,
      author_email=raspberryturk.__email__,
      url='https://bitbucket.com/joeymeyer/raspberryturk',
      packages=find_packages(),
      entry_points={
          'console_scripts': [
              'raspberryturk = raspberryturk.__main__:main'
          ]
      },
      classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Programming Language :: Python :: 2.7'
        ]
     )