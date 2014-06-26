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
from pyopencl.tools import VectorArg, ScalarArg, dtype_to_ctype

try:
    xrange = xrange
except:
    xrange = range


class ConstArg(VectorArg):
    def __init__(self, dtype, name):
        VectorArg.__init__(self, dtype, name, with_offset=True)

    def declarator(self):
        return "__global const %s *%s__base, long %s__offset" % (
            dtype_to_ctype(self.dtype), self.name, self.name)


def _dtype_is_double_complex(t):
    cplx = t.kind == 'c'
    if cplx and t not in (np.complex64, np.complex128):
        raise TypeError('Only complex64 and complex128 are supported.')
    return t in (np.float64, np.complex128), cplx


def _get_lin_comb_expr_fmts(t1, t2, tres, tbase=None):
    t1_dbl, t1_cplx = _dtype_is_double_complex(t1)
    t2_dbl, t2_cplx = _dtype_is_double_complex(t2)
    tres_dbl, tres_cplx = _dtype_is_double_complex(tres)
    if tbase:
        tbase_dbl, tbase_cplx = _dtype_is_double_complex(tbase)
    else:
        tbase_dbl = False
        tbase_cplx = False
    t1_fmt = '%s'
    t2_fmt = '%s'
    tbase_fmt = '%s'
    tres_fmt = '%s'
    # Down convert types if higher precision/complex part is not needed.
    if not tres_cplx:
        if t1_cplx:
            t1_cplx = False
            t1 = np.float64 if t1_dbl else np.float32
            t1_fmt = '((%s).x)'
        if t2_cplx:
            t2_cplx = False
            t2 = np.float64 if t2_dbl else np.float32
            t2_fmt = '((%s).x)'
        if tbase_cplx:
            tbase_cplx = False
            tbase = np.float64 if tbase_dbl else np.float32
            tbase_fmt = '((%s).x)'
    elif not tbase_cplx:
        if not (t1_cplx or t2_cplx):
            tres_fmt = ('(cdouble_t)((%s), 0)' if tres_dbl
                        else '(cfloat_t)((%s), 0)')
        else:
            tbase_fmt = ('(cdouble_t)((%s), 0)' if tres_dbl
                         else '(cfloat_t)((%s), 0)')
    if not tres_dbl:
        if t1_dbl:
            t1_dbl = False
            t1 = np.complex64 if t1_cplx else np.float32
            t1_fmt = ('cfloat_cast(%s)' if t1_cplx
                      else '((float)(%s))') % t1_fmt
        if t2_dbl:
            t2_dbl = False
            t2 = np.complex64 if t2_cplx else np.float32
            t2_fmt = ('cfloat_cast(%s)' if t2_cplx
                      else '((float)(%s))') % t2_fmt
        if tbase_dbl:
            tbase_dbl = False
            tbase = np.complex64 if tbase_cplx else np.float32
            tbase_fmt = ('cfloat_cast(%s)' if tbase_cplx
                         else '((float)(%s))') % tbase_fmt
    elif (tres_cplx and (t1_cplx or t2_cplx or tbase_cplx)
          and not (t1_dbl or t2_dbl or tbase_dbl)):
        tres_fmt = 'cdouble_cast(%s)' % tres_fmt

    if t1_cplx:
        if t2_cplx:
            if t1_dbl:
                if t2_dbl:
                    return (tres_fmt, 'cdouble_mul(%s, %s)' % (t1_fmt, t2_fmt),
                            tbase_fmt)
                return (tres_fmt, ('cdouble_mul(%s, cdouble_cast(%s))' %
                                   (t1_fmt, t2_fmt)), tbase_fmt)
            elif t2_dbl:
                return (tres_fmt, ('cdouble_mul(cdouble_cast(%s), %s)' %
                                   (t1_fmt, t2_fmt)), tbase_fmt)
            return (tres_fmt, ('cfloat_mul(%s, %s)' %
                               (t1_fmt, t2_fmt)), tbase_fmt)
        elif t1_dbl:
            return (tres_fmt, ('cdouble_mulr(%s, %s)' %
                               (t1_fmt, t2_fmt)), tbase_fmt)
        elif t2_dbl:
            return (tres_fmt, ('cdouble_mulr(cdouble_cast(%s), %s)' %
                               (t1_fmt, t2_fmt)), tbase_fmt)
        return (tres_fmt, ('cfloat_mulr(%s, %s)' %
                           (t1_fmt, t2_fmt)), tbase_fmt)
    elif t2_cplx:
        if t2_dbl:
            return (tres_fmt, ('cdouble_rmul(%s, %s)' %
                               (t1_fmt, t2_fmt)), tbase_fmt)
        elif t1_dbl:
            return (tres_fmt, ('cdouble_rmul(%s, cdouble_cast(%s))' %
                               (t1_fmt, t2_fmt)), tbase_fmt)
        return (tres_fmt, ('cfloat_rmul(%s, %s)' %
                           (t1_fmt, t2_fmt)), tbase_fmt)
    return (tres_fmt, ('(%s * %s)' % (t1_fmt, t2_fmt)), tbase_fmt)


def lin_comb_kernel(ctx, res_type, ary_type, weight_type, length, name=None):
    res_type = np.dtype(res_type)
    ary_type = np.dtype(ary_type)
    weight_type = np.dtype(weight_type)
    res_fmt, mul_fmt, _ = _get_lin_comb_expr_fmts(ary_type, weight_type,
                                                  res_type)
    mul_fmt = mul_fmt % ('ary%d[i]', 'weight%d')
    expr = ' + '.join((mul_fmt % (i, i)) for i in xrange(length))
    expr = res_fmt % expr
    name = name or 'lin_comb_kernel'
    return cl_elwise.get_elwise_kernel(
        ctx, [VectorArg(res_type, 'res', with_offset=True)] +
        [ConstArg(ary_type, 'ary%d' % i) for i in xrange(length)] +
        [ScalarArg(weight_type, 'weight%d' % i) for i in xrange(length)],
        'res[i] = ' + expr, name=name, auto_preamble=True)


def lin_comb_diff_kernel(ctx, res_type, base_type, ary_type, weight_type,
                         length, name=None):
    res_type = np.dtype(res_type)
    base_type = np.dtype(base_type)
    ary_type = np.dtype(ary_type)
    weight_type = np.dtype(weight_type)
    mul_fmt = get_mul_expr(ary_type, 'ary%d[i]', weight_type, 'weight%d')
    expr = ' + '.join((mul_fmt % (i, i)) for i in xrange(length))
    name = name or 'lin_comb_diff_kernel'
    return cl_elwise.get_elwise_kernel(
        ctx, [VectorArg(res_type, 'res', with_offset=True),
              ConstArg(base_type, 'base_ary')] +
        [ConstArg(ary_type, 'ary%d' % i) for i in xrange(length)] +
        [ScalarArg(weight_type, 'weight%d' % i) for i in xrange(length)],
        'res[i] = base_ary[i] + ' + expr, name=name, auto_preamble=True)
