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

from __future__ import print_function

from .elwise import lin_comb_diff_kernel, run_kernel as _run_elwise
from .utils import get_group_sizes, src_dir as cl_src_dir

import pyopencl as cl
import pyopencl.array as cl_array
from pyopencl.compyte.dtypes import dtype_to_ctype
import numpy as np
from six.moves import range as _range


def solve_ode(t0, t1, h, y0, f, queue, wait_for=None):
    ctx = queue.context
    dev = queue.device
    y_type = y0.dtype
    weight_type = (np.float64 if y_type in (np.float64, np.complex128)
                   else np.float32)
    nsteps = int((t1 - t0) / h)
    # Arrays for results in each steps
    ys = [cl_array.Array(queue, y0.shape, y_type, strides=y0.strides)
          for i in _range(nsteps + 1)]
    ks = [cl_array.Array(queue, y0.shape, y_type, strides=y0.strides)
          for i in _range(4)]
    tmp_y = cl_array.Array(queue, y0.shape, y_type, strides=y0.strides)
    total_size = ys[0].size
    # initialize
    prev_evt = cl.enqueue_copy(queue, ys[0].base_data, y0,
                               device_offset=ys[0].offset, is_blocking=False,
                               wait_for=wait_for)
    h_8 = h / 8.
    h3_8 = h * 3 / 8.
    h_3 = h / 3.
    h2_3 = h * 2 / 3.
    comb_knls = [lin_comb_diff_kernel(ctx, y_type, y_type, y_type, weight_type,
                                      i, name='ode_lin_diff_%d' % i)
                 for i in _range(1, 5)]
    g_size, l_size = get_group_sizes(total_size, dev, comb_knls[0])

    def _run_comb_knls(l, wait_for, *args):
        return _run_elwise(comb_knls[l], queue, g_size, l_size,
                           total_size, wait_for, *args)

    for i in _range(nsteps):
        prev_y = ys[i]
        next_y = ys[i + 1]
        tn = t0 + i * h
        prev_evt = f(tn, prev_y, ks[0], wait_for=[prev_evt])
        prev_evt = _run_comb_knls(0, [prev_evt], tmp_y, prev_y, ks[0], h_3)
        prev_evt = f(tn + h_3, tmp_y, ks[1], wait_for=[prev_evt])
        prev_evt = _run_comb_knls(1, [prev_evt], tmp_y, prev_y, ks[0], ks[1],
                                  -h_3, h)
        prev_evt = f(tn + h2_3, tmp_y, ks[2], wait_for=[prev_evt])
        prev_evt = _run_comb_knls(2, [prev_evt], tmp_y, prev_y, ks[0], ks[1],
                                  ks[2], h, -h, h)
        prev_evt = f(tn + h, tmp_y, ks[3], wait_for=[prev_evt])
        prev_evt = _run_comb_knls(3, [prev_evt], next_y, prev_y, ks[0], ks[1],
                                  ks[2], ks[3], h_8, h3_8, h3_8, h_8)
    return ys, prev_evt


_ode_solver_kernel_fmt = """

#define elwise_diff_func {elwise_diff_func}
#define T_TYPE {t_type}
#define Y_TYPE {y_type}
#define EXTRA_ARGS_DEC {extra_args_decl}
#define EXTRA_ARGS {extra_args_name}
#define elwise_post_func {post_func}
#define HAS_POST_FUNC {has_post_func}
#include <pyscical-ode.cl>
"""


class ElwiseOdeSolver(object):
    def __init__(self, ctx, dev, src, func_name, t_type=np.float32,
                 y_type=np.float32, extra_args=None, options=None,
                 post_func=None):
        t_type = np.dtype(t_type)
        y_type = np.dtype(y_type)
        if not extra_args:
            extra_args_decl = ''
            extra_args_name = ''
        else:
            extra_args_decl = ', ' + ', '.join(arg.decl for arg in extra_args)
            extra_args_name = ', ' + ', '.join(arg.name for arg in extra_args)
        solver_kernel_src = _ode_solver_kernel_fmt.format(
            elwise_diff_func=func_name,
            t_type=dtype_to_ctype(t_type),
            y_type=dtype_to_ctype(y_type),
            extra_args_decl=extra_args_decl,
            extra_args_name=extra_args_name,
            post_func=post_func or '',
            has_post_func='1' if post_func else '0')
        whole_src = src + solver_kernel_src

        options = (options or []) + ['-I', cl_src_dir + '/cl']
        self.__ctx = ctx
        self.__dev = dev
        self.__y_type = y_type
        self.__t_type = t_type
        self.__prog = cl.Program(ctx, whole_src)
        self.__prog.build(options=options, devices=[dev])
        self.__has_post = bool(post_func)

    def run(self, t0, t1, h, y0, queue, extra_args=(), wait_for=None):
        # TODO?
        # check y0 type?
        nsteps = int((t1 - t0) / h)
        # Arrays for results in each steps
        y_type = self.__y_type
        ys = [cl_array.Array(queue, y0.shape, y_type, strides=y0.strides)
              for i in _range(nsteps + 1)]
        ks = [cl_array.Array(queue, y0.shape, y_type, strides=y0.strides)
              for i in _range(3)]
        tmp_y1 = cl_array.Array(queue, y0.shape, y_type, strides=y0.strides)
        tmp_y2 = cl_array.Array(queue, y0.shape, y_type, strides=y0.strides)
        total_size = ys[0].size
        # initialize
        prev_evt = cl.enqueue_copy(queue, ys[0].base_data, y0,
                                   device_offset=ys[0].offset,
                                   is_blocking=False, wait_for=wait_for)
        it1_knl = self.__prog.pyscical_ode_solver_iter1
        it2_knl = self.__prog.pyscical_ode_solver_iter2
        it3_knl = self.__prog.pyscical_ode_solver_iter3
        it4_knl = self.__prog.pyscical_ode_solver_iter4
        if self.__has_post:
            post_knl = self.__prog.pyscical_ode_solver_post
        g_size, l_size = get_group_sizes(total_size, self.__dev, it1_knl)

        t_type = self.__t_type.type
        it1_knl.set_args(t_type(t0), t_type(h), ys[0].base_data,
                         ks[0].base_data, tmp_y1.base_data,
                         np.int64(total_size), *extra_args)
        it2_knl.set_args(t_type(t0), t_type(h), tmp_y1.base_data,
                         ks[0].base_data, ks[1].base_data,
                         tmp_y2.base_data, np.int64(total_size), *extra_args)
        it3_knl.set_args(t_type(t0), t_type(h), tmp_y2.base_data,
                         ks[0].base_data, ks[1].base_data, ks[2].base_data,
                         tmp_y1.base_data, np.int64(total_size), *extra_args)
        it4_knl.set_args(t_type(t0), t_type(h), tmp_y1.base_data,
                         ks[0].base_data, ks[1].base_data, ks[2].base_data,
                         ys[1].base_data, np.int64(total_size), *extra_args)
        if self.__has_post:
            post_knl.set_args(t_type(t0), t_type(h), ys[1].base_data,
                              np.int64(total_size), *extra_args)

        for i in _range(nsteps):
            t = t_type(i * h + t0)
            it1_knl.set_arg(0, t)
            it1_knl.set_arg(2, ys[i].base_data)
            prev_evt = cl.enqueue_nd_range_kernel(queue, it1_knl, g_size,
                                                  l_size, None, [prev_evt])

            it2_knl.set_arg(0, t)
            prev_evt = cl.enqueue_nd_range_kernel(queue, it2_knl, g_size,
                                                  l_size, None, [prev_evt])

            it3_knl.set_arg(0, t)
            prev_evt = cl.enqueue_nd_range_kernel(queue, it3_knl, g_size,
                                                  l_size, None, [prev_evt])

            it4_knl.set_arg(0, t)
            it4_knl.set_arg(6, ys[i + 1].base_data)
            prev_evt = cl.enqueue_nd_range_kernel(queue, it4_knl, g_size,
                                                  l_size, None, [prev_evt])
            if self.__has_post:
                post_knl.set_arg(0, t)
                post_knl.set_arg(2, ys[i + 1].base_data)
                prev_evt = cl.enqueue_nd_range_kernel(queue, post_knl, g_size,
                                                      l_size, None, [prev_evt])

        return ys, prev_evt
