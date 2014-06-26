#!/usr/bin/env python

import pytest
import numpy as np

import pyopencl as cl
from pyopencl.tools import (pytest_generate_tests_for_pyopencl as
                            pytest_generate_tests)

from pyscical.ocl.ode import solve_ode


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
