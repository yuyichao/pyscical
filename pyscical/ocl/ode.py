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

from .elwise import lin_comb_diff_kernel, run_kernel as run_elwise_kernel
from .utils import get_group_sizes

import pyopencl as cl
import pyopencl.array as cl_array
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
        return run_elwise_kernel(comb_knls[l], queue, g_size, l_size,
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
#define EXTRA_ARGS_DEC {extra_args_dec}
#define EXTRA_ARGS {extra_args}
#include <pyscical-ode.cl>
"""
