#!/usr/bin/env python

try:
    from setuptools import setup
except:
    from distutils.core import setup

setup(
    name='pyscical',
    version='0.1',
    description='Python Scientific Calculator Based on Pylab etc.',
    author='Yichao Yu',
    author_email='yyc1992@gmail.com',
    license='GPLv3',
    url='http://github.com/yuyichao/pyscical',
    packages=['pyscical'],
    package_dir={'': 'module'},
)
