#!/usr/bin/env python
#
# Copyright (C) 2012~2014 by Yichao Yu
# yyc1992@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# IPython Specifit stuff

__all__ = ['nb_save']

from os import path as _path
import sys

from IPython.utils import py3compat

ipython = get_ipython()


def nb_save(fname):
    hist_gen = ipython.history_manager.get_range()
    if not fname.endswith('.py'):
        fname += '.py'
    if _path.isfile(fname):
        ans = input('File `%s` exists. Overwrite (y/[N])? ' % fname)
        if ans.lower() not in ['y', 'yes']:
            print('Operation cancelled.')
            return
    with open(fname, 'w', encoding='utf-8') as f:
        f.write("#!%s\n" % sys.executable)
        f.write("# coding: utf-8\n")
        for hist in hist_gen:
            f.write(py3compat.cast_unicode(hist[2]) + '\n')
