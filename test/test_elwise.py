#!/usr/bin/env python

import pytest
import numpy as np

import pyopencl as cl
from pyopencl.tools import (pytest_generate_tests_for_pyopencl as
                            pytest_generate_tests)
from pyopencl.characterize import has_double_support
import pyopencl.array as cl_array

from pyscical.ocl.elwise import (lin_comb_kernel, lin_comb_diff_kernel,
                                 get_group_sizes,
                                 run_kernel as run_elwise_kernel)


@pytest.mark.parametrize("res_type", [np.float32, np.float64,
                                      np.complex64, np.complex128])
@pytest.mark.parametrize("arg_type", [np.float32, np.float64,
                                      np.complex64, np.complex128])
@pytest.mark.parametrize("weight_type", [np.float32, np.float64,
                                         np.complex64, np.complex128])
def test_get_kernels(ctx_factory, res_type, arg_type, weight_type):
    ctx = ctx_factory()
    dev, = ctx.devices
    if not has_double_support(dev):
        for t in res_type, arg_type, weight_type:
            if t in (np.float64, np.complex128):
                pytest.skip('Device does not support double.')
    for length in range(1, 3):
        lin_comb_kernel(ctx, res_type, arg_type, weight_type, length)


@pytest.mark.parametrize("res_type", [np.float32, np.float64,
                                      np.complex64, np.complex128])
@pytest.mark.parametrize("arg_type", [np.float32, np.float64,
                                      np.complex64, np.complex128])
@pytest.mark.parametrize("weight_type", [np.float32, np.float64,
                                         np.complex64, np.complex128])
@pytest.mark.parametrize("base_type", [np.float32, np.float64,
                                       np.complex64, np.complex128])
def test_get_diff_kernels(ctx_factory, res_type, base_type,
                          arg_type, weight_type):
    ctx = ctx_factory()
    dev, = ctx.devices
    if not has_double_support(dev):
        for t in res_type, arg_type, weight_type, base_type:
            if t in (np.float64, np.complex128):
                pytest.skip('Device does not support double.')
    for length in range(1, 3):
        lin_comb_diff_kernel(ctx, res_type, base_type, arg_type,
                             weight_type, length)


@pytest.mark.parametrize("arg_type", [np.float32, np.float64,
                                      np.complex64, np.complex128])
def test_lin_comb(ctx_factory, arg_type):
    ctx = ctx_factory()
    dev, = ctx.devices
    if not has_double_support(dev):
        if arg_type in (np.float64, np.complex128):
            pytest.skip('Device does not support double.')
    n = 100000
    a_np = (np.random.randn(n) * 10).astype(arg_type)
    b_np = (np.random.randn(n) * 10).astype(arg_type)
    queue = cl.CommandQueue(ctx)

    a_g = cl.array.to_device(queue, a_np)
    b_g = cl.array.to_device(queue, b_np)
    res_g = cl.array.empty_like(a_g)
    lin_comb = lin_comb_kernel(ctx, arg_type, arg_type, np.float32, 2)
    gs, ls = get_group_sizes(n, dev, lin_comb)

    evt = run_elwise_kernel(lin_comb, queue, gs, ls, n, [],
                            res_g, a_g, b_g, 2, 3)
    evt.wait()

    # Check on GPU with PyOpenCL Array:
    assert np.linalg.norm((res_g - (2 * a_g + 3 * b_g)).get()) == 0

    # Check on CPU with Numpy:
    res_np = res_g.get()
    assert np.linalg.norm(res_np - (2 * a_np + 3 * b_np)) == 0


@pytest.mark.parametrize("arg_type", [np.float32, np.float64,
                                      np.complex64, np.complex128])
def test_lin_comb_diff(ctx_factory, arg_type):
    ctx = ctx_factory()
    dev, = ctx.devices
    if not has_double_support(dev):
        if arg_type in (np.float64, np.complex128):
            pytest.skip('Device does not support double.')
    n = 100000
    a_np = (np.random.randn(n)).astype(arg_type)
    b_np = (np.random.randn(n)).astype(arg_type)
    c_np = (np.random.randn(n) * 10).astype(arg_type)
    queue = cl.CommandQueue(ctx)

    a_g = cl.array.to_device(queue, a_np)
    b_g = cl.array.to_device(queue, b_np)
    c_g = cl.array.to_device(queue, c_np)
    res_g = cl.array.empty_like(a_g)
    lin_comb_diff = lin_comb_diff_kernel(ctx, arg_type, arg_type,
                                         arg_type, np.float32, 2)
    gs, ls = get_group_sizes(n, dev, lin_comb_diff)

    evt = run_elwise_kernel(lin_comb_diff, queue, gs, ls, n, [],
                            res_g, c_g, a_g, b_g, 2, 3)
    evt.wait()

    # Check on GPU with PyOpenCL Array:
    assert np.linalg.norm((res_g - (c_g + 2 * a_g + 3 * b_g)).get()) <= 1e-4

    # Check on CPU with Numpy:
    res_np = res_g.get()
    assert np.linalg.norm(res_np - (c_np + 2 * a_np + 3 * b_np)) <= 1e-4
