#!/usr/bin/env python

# Copyright 2012 Yu Yichao
# yyc1992@gmail.com
#
# This file is part of PySciCal.
#
# PySciCal is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PySciCal is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with PySciCal.  If not, see <http://www.gnu.org/licenses/>.

# IPython Specifit stuff

from IPython.utils import py3compat
import os

ipython = get_ipython()

def nb_save(fname):
    hist_gen = ipython.shell.history_manager.get_range()
    if not fname.endswith('.py'):
        fname += '.py'
    if os.path.isfile(fname):
        ans = input('File `%s` exists. Overwrite (y/[N])? ' % fname)
        if ans.lower() not in ['y','yes']:
            print('Operation cancelled.')
            return
    with open(fname, 'w', encoding='utf-8') as f:
        f.write("# coding: utf-8\n")
        for hist in hist_gen:
            f.write(py3compat.cast_unicode(hist[2]) + '\n')
