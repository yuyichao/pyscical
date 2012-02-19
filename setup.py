#!/usr/bin/env python

try:
    # First try to load most advanced setuptools setup.
    from setuptools import setup
except:
    # Fall back if setuptools is not installed.
    from distutils.core import setup

setup(
    name='pyscical',
    version='0.1',
    description='Python Scientific Calculator Based on Pylab etc.',
    author='Yichao Yu',
    author_email='yyc1992@gmail.com',
    license='GPLv3',
    url='http://github.com/yuyichao/pyscical',
    py_modules=['pyscical'],
    package_dir={'': 'module'},
)
