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

import numpy as np

def cffi_ptr(obj, _ffi, writable=False, retain=False):
    if isinstance(obj, bytes):
        if writable:
            # bytes is not writable
            raise TypeError('expected an object with a writable '
                            'buffer interface.')
        if retain:
            buf = _ffi.new('char[]', obj)
            return (buf, len(obj), buf)
        return (obj, len(obj), obj)
    elif isinstance(obj, np.ndarray):
        # numpy array
        return (_ffi.cast('void*', obj.__array_interface__['data'][0]),
                obj.nbytes, obj)
    elif isinstance(obj, np.generic):
        if writable or retain:
            raise TypeError('expected an object with a writable '
                            'buffer interface.')
        # numpy scalar
        #
        # * obj.__array_interface__ exists in CPython although requires
        #   holding a reference to the dynamically created
        #   __array_interface__ object
        #
        # * does not exist (yet?) in numpypy.
        s_array = obj[()]
        return (_ffi.cast('void*', s_array.__array_interface__['data'][0]),
                s_array.nbytes, s_array)
    raise TypeError("Only numpy arrays and bytes can be converted")
