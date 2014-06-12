#!/usr/bin/env python
#
# Copyright (C) 2014~2014 by Yichao Yu
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

from cffi import FFI
from os import path as _path

_ffi = FFI()
_basedir = _path.dirname(__file__)

def _get_api_header():
    with open(_path.join(_basedir, 'api.h')) as f:
        return f.read()

_ffi.cdef(_get_api_header())

def _import_library():
    names = list(_get_wrapcl_so_names())
    for name in names:
        try:
            return _ffi.dlopen(name)
        except OSError:
            pass

    raise RuntimeError("could not find PyOpenCL wrapper library. (tried: %s)"
        % ", ".join(names))

_lib = _ffi.dlopen(_path.join(_basedir, '_pyscical.so'))
