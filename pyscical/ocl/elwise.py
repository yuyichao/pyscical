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

import numpy as np

import pyopencl as cl
import pyopencl.elementwise as cl_elwise
import pyopencl.array as cl_array
from pyopencl.tools import VectorArg, ScalarArg

try:
    xrange = xrange
except:
    xrange = range


def _get_mul_expr_fmt(t1, t2):
    if t1.kind == 'c':
        if t1.itemsize not in (8, 16):
            raise TypeError('Only complex64 and complex128 are supported.')
        t1_is_double = t1.itemsize == 16
        if t2.kind == 'c':
            if t2.itemsize not in (8, 16):
                raise TypeError('Only complex64 and complex128 are supported.')
            t2_is_double = t2.itemsize == 16
            if t1_is_double:
                if t2_is_double:
                    return 'cdouble_mul(%s, %s)'
                return 'cdouble_mul(%s, cdouble_cast(%s))'
            elif t2_is_double:
                return 'cdouble_mul(cdouble_cast(%s), %s)'
            return 'cfloat_mul(%s, %s)'
        elif t1_is_double:
            return 'cdouble_mulr(%s, %s)'
        elif t2.itemsize >= 8:
            return 'cdouble_mulr(cdouble_cast(%s), %s)'
        return 'cfloat_mulr(%s, %s)'
    elif t2.kind == 'c':
        if t2.itemsize not in (8, 16):
            raise TypeError('Only complex64 and complex128 are supported.')
        elif t2.itemsize == 16:
            return 'cdouble_rmul(%s, %s)'
        elif t1.itemsize == 8:
            return 'cdouble_rmul(%s, cdouble_cast(%s))'
        return 'cfloat_rmul(%s, %s)'
    return '(%s * %s)'


def get_mul_expr(t1, name1, t2, name2):
    return _get_mul_expr_fmt(t1, t2) % (name1, name2)


def lin_comb_kernel(ctx, res_type, ary_type, weight_type, length, name=None):
    res_type = np.dtype(res_type)
    ary_type = np.dtype(ary_type)
    weight_type = np.dtype(weight_type)
    mul_fmt = get_mul_expr(ary_type, 'ary%d[i]', weight_type, 'weight%d[i]')
    expr = ' + '.join((mul_fmt % (i, i)) for i in xrange(length))
    name = name or 'lin_comb_kernel'
    return cl_elwise.get_elwise_kernel(
        ctx, [VectorArg(res_type, 'res', with_offset=True)] +
        [VectorArg(ary_type, 'ary%d' % i) for i in xrange(length)] +
        [ScalarArg(weight_type, 'weight%d' % i) for i in xrange(length)],
        'res[i] = ' + expr, name=name, auto_preamble=True)
