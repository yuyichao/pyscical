#!/usr/bin/env python

from __future__ import division

import pytest
import numpy as np
from os import path as _path

import pyopencl as cl
import pyopencl.elementwise as cl_elwise
import pyopencl.array as cl_array
from pyopencl.tools import (VectorArg, ScalarArg,
                            pytest_generate_tests_for_pyopencl as
                            pytest_generate_tests)

from pyscical.ocl.ode import solve_ode, ElwiseOdeSolver
from pyscical.ocl.elwise import ConstArg, run_kernel as run_elwise_kernel
from pyscical.ocl.utils import get_group_sizes, CLArg

def main():
    ctx = cl.create_some_context()
    queue = cl.CommandQueue(ctx)
    dev = queue.device
    src = """
    #include <wave_func.cl>
    static float
    _calc_wave_func(float t, const __global float *y_in, size_t i, float y_in_i,
                    float h_x, ulong len_x)
    {
        return calc_wave_func(y_in, h_x, len_x, i);
    }
    """
    solver = ElwiseOdeSolver(ctx, dev, src, "_calc_wave_func",
                             extra_args=(CLArg('h_x', 'float'),
                                         CLArg('len_x', 'ulong')),
                             options=['-I', _path.dirname(__file__)])

    t0 = 0
    t1 = 1000
    h = 0.2

    h_x = 0.2
    len_x = 256

    xs = np.arange(len_x) * np.pi / (len_x - 1)
    y0 = np.r_[(np.sin(xs) + np.sin(xs * 2) + np.sin(xs * 3)
                + np.sin(xs * 4) + np.sin(xs * 5)) / 5,
               np.zeros(len_x)].astype(np.float32)
    # y0 += np.r_[np.zeros(len_x),
    #             [(min((i / len_x) - 0.4, 0.5 - (i / len_x)) * 20
    #               if 0.4 < (i / len_x) < 0.5 else 0)
    #               for i in range(len_x)]].astype(np.float32)
    y0 += np.r_[np.zeros(len_x),
                [((i / len_x) - 0.2 if 0.15 < (i / len_x) < 0.25 else 0) * 20
                 for i in range(len_x)]].astype(np.float32)
    # y0 = np.r_[[(1 if 0.4 < (i / len_x) < 0.5 else 0)
    #             for i in range(len_x)],
    #            np.zeros(len_x)].astype(np.float32)
    y0 += np.r_[[(1 if 0.75 < (i / len_x) < 0.85 else 0)
                 for i in range(len_x)],
                np.zeros(len_x)].astype(np.float32)

    res, evt = solver.run(t0, t1, h, y0, queue,
                          extra_args=(np.float32(h_x), np.int64(len_x)))
    evt.wait()
    res_np = [a.get() for a in res]
    from pylab import plot, show, imshow, figure, colorbar, xlabel, ylabel
    from pylab import legend, title, savefig, close, grid, xlim, ylim
    from matplotlib import animation
    fig = figure()
    line, = plot([], [], linewidth=2, linestyle='-', marker='.')
    xlim(0, len(res_np[0]))
    ylim(-2, 2)

    def init():
        line.set_data([], [])
        return line,

    def animate(i):
        x = np.arange(len(res_np[i]))
        y = res_np[i]
        line.set_data(x, y)
        return line,
    anim = animation.FuncAnimation(fig, animate, init_func=init,
                                   frames=len(res_np),
                                   interval=10, blit=True)
    # anim.save('wave.mp4', fps=100)
    grid()
    show()


def _get_wave_kernel(ctx):
    return cl_elwise.get_elwise_kernel(
        ctx, [VectorArg(np.float32, 'res', with_offset=True),
              ConstArg(np.float32, 'in'),
              ScalarArg(np.float32, 'h'), ScalarArg(np.int32, 'len')],
        'res[i] = calc_wave_func(in, h, len, i)',
        preamble="#include <wave_func.cl>",
        options=['-I', _path.dirname(__file__)])


def main2():
    ctx = cl.create_some_context()
    queue = cl.CommandQueue(ctx)
    dev = queue.device
    knl = _get_wave_kernel(ctx)

    t0 = 0
    t1 = 1000
    h = 0.2

    h_x = 0.2
    len_x = 256

    gs, ls = get_group_sizes(len_x * 2, dev, knl)

    def f(t, y_in, y_out, wait_for=None):
        return run_elwise_kernel(knl, queue, gs, ls, len_x * 2, wait_for,
                                 y_out, y_in, h_x, len_x)

    xs = np.arange(len_x) * np.pi / (len_x - 1)
    y0 = np.r_[(np.sin(xs) + np.sin(xs * 2) + np.sin(xs * 3)
                + np.sin(xs * 4) + np.sin(xs * 5)) / 5,
               np.zeros(len_x)].astype(np.float32)
    # y0 += np.r_[np.zeros(len_x),
    #             [(min((i / len_x) - 0.4, 0.5 - (i / len_x)) * 20
    #               if 0.4 < (i / len_x) < 0.5 else 0)
    #               for i in range(len_x)]].astype(np.float32)
    y0 += np.r_[np.zeros(len_x),
                [((i / len_x) - 0.2 if 0.15 < (i / len_x) < 0.25 else 0) * 20
                 for i in range(len_x)]].astype(np.float32)
    # y0 = np.r_[[(1 if 0.4 < (i / len_x) < 0.5 else 0)
    #             for i in range(len_x)],
    #            np.zeros(len_x)].astype(np.float32)
    y0 += np.r_[[(1 if 0.75 < (i / len_x) < 0.85 else 0)
                 for i in range(len_x)],
                np.zeros(len_x)].astype(np.float32)

    res, evt = solve_ode(t0, t1, h, y0, f, queue)
    evt.wait()
    res_np = [a.get() for a in res]
    from pylab import plot, show, imshow, figure, colorbar, xlabel, ylabel
    from pylab import legend, title, savefig, close, grid, xlim, ylim
    from matplotlib import animation
    fig = figure()
    line, = plot([], [], linewidth=2, linestyle='-', marker='.')
    xlim(0, len(res_np[0]))
    ylim(-2, 2)

    def init():
        line.set_data([], [])
        return line,

    def animate(i):
        x = np.arange(len(res_np[i]))
        y = res_np[i]
        line.set_data(x, y)
        return line,
    anim = animation.FuncAnimation(fig, animate, init_func=init,
                                   frames=len(res_np),
                                   interval=10, blit=True)
    # anim.save('wave.mp4', fps=100)
    grid()
    show()

if __name__ == '__main__':
    main()
    # main2()
