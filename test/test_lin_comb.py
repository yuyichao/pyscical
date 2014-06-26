#!/usr/bin/env python

import pytest
import numpy as np

import pyopencl as cl
from pyopencl.tools import (pytest_generate_tests_for_pyopencl as
                            pytest_generate_tests)
from pyopencl.characterize import has_double_support

from pyscical.ocl.elwise import lin_comb_kernel, lin_comb_diff_kernel


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
    for length in range(1, 4):
        lin_comb_kernel(ctx, res_type, arg_type, weight_type, length)
