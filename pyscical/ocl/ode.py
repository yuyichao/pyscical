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

from . import elwise

import pyopencl as cl
import pyopencl.array as cl_array
import numpy as np

try:
    xrange = xrange
except:
    xrange = range


def get_group_sizes(dev, n, limit):
    max_work_items = limit
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


def _run_kernel(knl, queue, gs, ls, size, wait_for, *args, **kws):
    wait_for = list(wait_for) if wait_for else []

    actual_args = []
    for arg in args:
        if isinstance(arg, Array):
            actual_args.append(arg.base_data)
            actual_args.append(arg.offset)
            wait_for.extend(arg.events)
        else:
            actual_args.append(arg)
        actual_args.append(size)

    return knl(queue, gs, ls, *actual_args, wait_for=wait_for)


def solve_ode(t0, t1, h, y0, f, queue):
    ctx = queue.context
    dev = queue.device
    y_type = y0.dtype
    weight_type = (np.float64 if y_type in (np.float64, np.complex128)
                   else np.float32)
    nsteps = (t1 - t0) // h
    # Arrays for results in each steps
    ys = [cl_array.Array(queue, y0.shape, y_type, strides=y0.strides)
          for i in xrange(nsteps + 1)]
    ks = [cl_array.Array(queue, y0.shape, y_type, strides=y0.strides)
          for i in xrange(4)]
    tmp_y = cl_array.Array(queue, y0.shape, y_type, strides=y0.strides)
    total_size = ys[0].size
    # initialize
    prev_evt = cl.enqueue_copy(queue, ys[0].base_data, y0,
                               device_offset=ys[0].offset, is_blocking=False)
    h_8 = h / 8.
    h3_8 = h * 3 / 8.
    h_3 = h / 3.
    h2_3 = h * 2 / 3.
    comb_knls = [elwise.lin_comb_diff_kernel(ctx, y_type, y_type, y_type,
                                             weight_type, i,
                                             name='ode_lin_diff_%d' % i)
                 for i in xrange(1, 5)]
    max_group_size = min(
        comb_knls[0].get_work_group_info(
            cl.kernel_work_group_info.WORK_GROUP_SIZE, dev),
        dev.max_work_group_size)
    g_size, l_size = get_group_sizes(dev, total_size, max_group_size)

    def _run_comb_knls(l, wait_for, *args):
        return _run_kernel(comb_knls[l], queue, g_size, l_size, total_size,
                           wait_for, *args)

    for i in xrange(n_steps):
        prev_y = ys[i]
        next_y = ys[i + 1]
        tn = t0 + i * h
        prev_evt = f(tn, prev_y, ks[0], wait_for=[prev_evt])
        prev_evt = _run_comb_knls(0, [prev_evt], tmp_y, prev_y, ks[0], h_3)
        prev_evt = f(tn + h_3, tmp_y, ks[1], wait_for=[prev_evt])
        prev_evt = _run_comb_knls(1, [prev_evt], tmp_y, prev_y, ks[0], -h_3,
                                  ks[1], h)
        prev_evt = f(tn + h2_3, tmp_y, ks[2], wait_for=[prev_evt])
        prev_evt = _run_comb_knls(2, [prev_evt], tmp_y, prev_y, ks[0], h,
                                  ks[1], -h, ks[2], h)
        prev_evt = f(tn + h, tmp_y, ks[3], wait_for=[prev_evt])
        prev_evt = _run_comb_knls(3, [prev_evt], next_y, prev_y, ks[0], h_8,
                                  ks[1], h3_8, ks[2], h3_8, ks[3], h_8)
    return ys, prev_evt