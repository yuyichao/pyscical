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


def _get_mul_expr_fmt(t1_dbl, t1_cplx, t2_dbl, t2_cplx):
    if t1_cplx:
        if t2_cplx:
            if t1_dbl:
                if t2_dbl:
                    return 'cdouble_mul(%s, %s)'
                return 'cdouble_mul(%s, cdouble_cast(%s))'
            elif t2_dbl:
                return 'cdouble_mul(cdouble_cast(%s), %s)'
            return 'cfloat_mul(%s, %s)'
        elif t1_dbl:
            return 'cdouble_mulr(%s, %s)'
        elif t2_dbl:
            return 'cdouble_mulr(cdouble_cast(%s), %s)'
        return 'cfloat_mulr(%s, %s)'
    elif t2_cplx:
        if t2_dbl:
            return 'cdouble_rmul(%s, %s)'
        elif t1_dbl:
            return 'cdouble_rmul(%s, cdouble_cast(%s))'
        return 'cfloat_rmul(%s, %s)'
    return '(%s * %s)'


def _get_convert_fmt(tres_dbl, tres_cplx, orig_dbl, orig_cplx):
    if tres_cplx:
        if tres_dbl:
            if not orig_cplx:
                return '((cdouble_t)(%s, 0))'
            elif not orig_dbl:
                return 'cdouble_cast(%s)'
            return '%s'
        elif not orig_cplx:
            return '((cfloat_t)%s)'
    return '%s'


def _get_lin_comb_expr_fmts(t1, t2, tres, tbase=None):
    t1_dbl, t1_cplx = _dtype_is_double_complex(t1)
    t1_fmt = '%s'
    t2_dbl, t2_cplx = _dtype_is_double_complex(t2)
    tres_dbl, tres_cplx = _dtype_is_double_complex(tres)
    t2_fmt = '%s'

    if tbase is not None:
        tbase_dbl, tbase_cplx = _dtype_is_double_complex(tbase)
        tbase_fmt = '%s'
    else:
        tbase_dbl = False
        tbase_cplx = False
    # Down convert types if higher precision/complex part is not needed.
    if not tres_cplx:
        if t1_cplx:
            t1_cplx = False
            t1 = np.float64 if t1_dbl else np.float32
            t1_fmt = '(%s.x)'
        if t2_cplx:
            t2_cplx = False
            t2 = np.float64 if t2_dbl else np.float32
            t2_fmt = '(%s.x)'
        if tbase_cplx:
            tbase_cplx = False
            tbase = np.float64 if tbase_dbl else np.float32
            tbase_fmt = '(%s.x)'
    if not tres_dbl:
        if t1_dbl:
            t1_dbl = False
            t1 = np.complex64 if t1_cplx else np.float32
            t1_fmt = ('cfloat_cast(%s)' if t1_cplx
                      else '((float)%s)') % t1_fmt
        if t2_dbl:
            t2_dbl = False
            t2 = np.complex64 if t2_cplx else np.float32
            t2_fmt = ('cfloat_cast(%s)' if t2_cplx
                      else '((float)%s)') % t2_fmt
        if tbase_dbl:
            tbase_dbl = False
            tbase = np.complex64 if tbase_cplx else np.float32
            tbase_fmt = ('cfloat_cast(%s)' if tbase_cplx
                         else '((float)%s)') % tbase_fmt

    mul_fmt = (_get_mul_expr_fmt(t1_dbl, t1_cplx,
                                 t2_dbl, t2_cplx) % (t1_fmt, t2_fmt))
    tres_fmt = _get_convert_fmt(tres_dbl, tres_cplx, t1_dbl or t2_dbl,
                                t1_cplx or t2_cplx)
    tbase_fmt = (_get_convert_fmt(tres_dbl, tres_cplx,
                                  tbase_dbl, tbase_cplx) % tbase_fmt
                 if tbase is not None else '%s')
    return tres_fmt, mul_fmt, tbase_fmt


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

    res_fmt, mul_fmt, base_fmt = _get_lin_comb_expr_fmts(ary_type, weight_type,
                                                         res_type, base_type)
    mul_fmt = mul_fmt % ('ary%d[i]', 'weight%d')
    expr = ' + '.join((mul_fmt % (i, i)) for i in xrange(length))
    expr = base_fmt % 'base_ary[i]' + ' + ' + res_fmt % expr

    name = name or 'lin_comb_diff_kernel'
    return cl_elwise.get_elwise_kernel(
        ctx, [VectorArg(res_type, 'res', with_offset=True),
              ConstArg(base_type, 'base_ary')] +
        [ConstArg(ary_type, 'ary%d' % i) for i in xrange(length)] +
        [ScalarArg(weight_type, 'weight%d' % i) for i in xrange(length)],
        'res[i] = ' + expr, name=name, auto_preamble=True)


def get_group_sizes(n, dev, kernel=None):
    max_work_items = dev.max_work_group_size
    if kernel is not None:
        max_work_items = min(
            max_work_items, kernel.get_work_group_info(
                cl.kernel_work_group_info.WORK_GROUP_SIZE, dev))
    min_work_items = min(32, max_work_items)
    max_groups = dev.max_compute_units * 4 * 8
    # 4 to overfill the device
    # 8 is an Nvidia constant--that's how many
    # groups fit onto one compute device

    if n < min_work_items:
        group_count = 1
        work_items_per_group = min_work_items
    elif n < (max_groups * min_work_items):
        group_count = (n + min_work_items - 1) // min_work_items
        work_items_per_group = min_work_items
    elif n < (max_groups * max_work_items):
        group_count = max_groups
        grp = (n + min_work_items - 1) // min_work_items
        work_items_per_group = (
            (grp + max_groups - 1) // max_groups) * min_work_items
    else:
        group_count = max_groups
        work_items_per_group = max_work_items

    return (group_count * work_items_per_group,), (work_items_per_group,)


def run_kernel(knl, queue, gs, ls, size, wait_for, *args, **kws):
    wait_for = list(wait_for) if wait_for else []

    actual_args = []
    for arg in args:
        if isinstance(arg, cl_array.Array):
            actual_args.append(arg.base_data)
            actual_args.append(arg.offset)
            wait_for.extend(arg.events)
        else:
            actual_args.append(arg)
    actual_args.append(size)

    return knl(queue, gs, ls, *actual_args, wait_for=wait_for)
