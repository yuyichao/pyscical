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

from .constants import *
try:
    from numba import jit
except:
    def jit(signature_or_function=None, *args, **kwargs):
        if callable(signature_or_function):
            return signature_or_function
        return lambda func: func

@jit('f8(f8, f8, f8, f8, f8)', nopython=True)
def compose_g(J_sum, J1, J2, g1, g2):
    if not J_sum:
        return 0.0
    J_sum_2 = J_sum * (J_sum + 1)
    J1_2 = J1 * (J1 + 1)
    J2_2 = J2 * (J2 + 1)
    return (g1 * (J_sum_2 + J1_2 - J2_2) +
            g2 * (J_sum_2 + J2_2 - J1_2)) / 2 / J_sum_2

@jit('f8(f8, f8, f8)', nopython=True)
def compose_gJ(J, L, S):
    return compose_g(J, L, S, 1.0, g_e)

@jit('f8(f8, f8, f8, f8, f8, f8)', nopython=True)
def _compose_gF(F, I, J, L, S, g_I):
    return compose_g(F, I, J, g_I, compose_gJ(J, L, S))

def compose_gF(F, I, J, L, S, g_I=0.0):
    return _compose_gF(F, I, J, L, S, g_I)
