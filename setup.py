#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='raspberryturk',
      version='0.0.1',
      description='Python package powering the Raspberry Turk chess-playing robot.',
      author='Joey Meyer',
      author_email='jmeyer41@gmail.com',
      url='https://bitbucket.com/joeymeyer/raspberryturk',
      packages=find_packages(),
      classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Programming Language :: Python :: 2.7'
        ]
     )