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

from pyscical.ocl.ode import solve_ode
from pyscical.ocl.elwise import (ConstArg, get_group_sizes,
                                 run_kernel as run_elwise_kernel)


def _get_harmonic_kernel(ctx):
    prg = cl.Program(ctx, """
    __kernel void
    harmonic(__global const float *in, __global float *out)
    {
        out[0] = in[1];
        out[1] = -in[0];
    }
    """).build()
    return prg.harmonic


def test_harmonic(ctx_factory):
    ctx = ctx_factory()
    queue = cl.CommandQueue(ctx)
    knl = _get_harmonic_kernel(ctx)
    start_evt = cl.UserEvent(ctx)

    def f(t, y_in, y_out, wait_for=None):
        knl.set_args(y_in.base_data, y_out.base_data)
        return cl.enqueue_task(queue, knl, wait_for=wait_for + [start_evt])

    t0 = 0
    t1 = 40
    h = 0.05
    y0 = np.array([1, 0]).astype(np.float32)
    res, evt = solve_ode(t0, t1, h, y0, f, queue)
    # Make sure the work is done asynchronously
    start_evt.set_status(cl.command_execution_status.COMPLETE)
    _res = [a.get() for a in res]
    evt.wait()
    res_np = np.array(_res).T
    ts = t0 + np.arange(len(res)) * h
    expect0 = np.cos(ts)
    expect1 = -np.sin(ts)

    assert np.linalg.norm(res_np[0] - expect0) < 1e-4
    assert np.linalg.norm(res_np[1] - expect1) < 1e-4


def _get_wave_kernel(ctx):
    return cl_elwise.get_elwise_kernel(
        ctx, [VectorArg(np.float32, 'res', with_offset=True),
              ConstArg(np.float32, 'in'),
              ScalarArg(np.float32, 'h'), ScalarArg(np.int32, 'len')],
        'calc_wave_func(res, in, h, len, i)',
        preamble="#include <wave_func.cl>",
        options=['-I', _path.dirname(__file__)])


def test_wave(ctx_factory):
    ctx = ctx_factory()
    queue = cl.CommandQueue(ctx)
    dev = queue.device
    knl = _get_wave_kernel(ctx)

    t0 = 0
    t1 = 100
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
    # from pylab import plot, show, imshow, figure, colorbar, xlabel, ylabel
    # from pylab import legend, title, savefig, close, grid, xlim, ylim
    # from matplotlib import animation
    # fig = figure()
    # line, = plot([], [], linewidth=2, linestyle='-', marker='.')
    # xlim(0, len(res_np[0]))
    # ylim(-2, 2)

    # def init():
    #     line.set_data([], [])
    #     return line,

    # def animate(i):
    #     x = np.arange(len(res_np[i]))
    #     y = res_np[i]
    #     line.set_data(x, y)
    #     return line,
    # anim = animation.FuncAnimation(fig, animate, init_func=init,
    #                                frames=len(res_np),
    #                                interval=10, blit=True)
    # # anim.save('wave.mp4', fps=100)
    # grid()
    # show()
    # ts = t0 + np.arange(len(res)) * h
    # expect0 = np.cos(ts)
    # expect1 = -np.sin(ts)
    # assert np.linalg.norm(res_np[0] - expect0) < 1e-4
    # assert np.linalg.norm(res_np[1] - expect1) < 1e-4


def _get_bloch_kernel(ctx):
    return cl_elwise.get_elwise_kernel(
        ctx, [VectorArg(np.complex64, 'res', with_offset=True),
              ConstArg(np.complex64, 'in'), ScalarArg(np.float32, 't'),
              ScalarArg(np.float32, 'slope'), ScalarArg(np.int32, 'len')],
        'calc_bloch_wave(res, in, t, slope, len, i)',
        preamble="#include <bloch_wave.cl>",
        options=['-I', _path.dirname(__file__)])


def test_bloch(ctx_factory):
    ctx = ctx_factory()
    queue = cl.CommandQueue(ctx)
    dev = queue.device
    if dev.type != cl.device_type.GPU:
        pytest.skip('Only use GPU')
    knl = _get_bloch_kernel(ctx)

    t0 = 0
    t1 = 550
    h = 0.02

    len_x = 512
    t_x = 1
    slope = 0.05
    # slope = 0

    gs, ls = get_group_sizes(len_x, dev, knl)

    def f(t, y_in, y_out, wait_for=None):
        return run_elwise_kernel(knl, queue, gs, ls, len_x, wait_for,
                                 y_out, y_in, t_x, slope, len_x)

    y0 = np.zeros(len_x).astype(np.complex64)
    # y0[int(len_x / 2)] = 1

    # y0[int(len_x * 2 / 5)] = np.sqrt(2) / 2
    # y0[int(len_x * 3 / 5)] = np.sqrt(2) / 2

    y0[int(len_x * 2 / 5)] = 1 / np.sqrt(3)
    y0[int(len_x / 2)] = 1 / np.sqrt(3)
    y0[int(len_x * 3 / 5)] = 1 / np.sqrt(3)

    print('start')
    res, evt = solve_ode(t0, t1, h, y0, f, queue)
    print('wait')
    evt.wait()
    print('done')
    dn = 19
    res_np = [np.abs(a.get()) for a in res[::dn]]
    # for a in res_np:
    #     a /= max(a)
    from pylab import plot, show, imshow, figure, colorbar, xlabel, ylabel
    from pylab import legend, title, savefig, close, grid, xlim, ylim, draw
    from matplotlib import animation
    # imshow(res_np[:500], vmax=0.2)
    # colorbar()
    # xlabel('Lattice sites')
    # ylabel('Time')
    # savefig('bloch3.png')
    # show()
    # fig = figure()
    # title('frame: 0')
    # # line, = plot([], [], linewidth=.5, linestyle='-', marker='.')
    # line, = plot([], [])
    # xlim(0, len(res_np[0]))
    # ylim(0, 1 / np.sqrt(3))
    # xlabel('Lattice sites')
    # ylabel('Amplitude')
    # grid()

    # def init():
    #     line.set_data([], [])
    #     return line,

    # def animate(i):
    #     title('frame: %d' % (i * dn))
    #     draw()
    #     x = np.arange(len(res_np[i]))
    #     y = res_np[i]
    #     line.set_data(x, y)
    #     return line,
    # anim = animation.FuncAnimation(fig, animate, init_func=init,
    #                                frames=len(res_np),
    #                                interval=dn, blit=True)
    # anim.save('bloch2.webm', fps=int(1000 / dn), bitrate=1000,
    #           extra_args=['-f', 'webm', '-vcodec', 'libvpx'])
    # show()
