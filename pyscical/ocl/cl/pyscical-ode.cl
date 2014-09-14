/**
 * Copyright (C) 2014~2014 by Yichao Yu
 * yyc1992@gmail.com
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

// elwise_diff_func
// T_TYPE
// Y_TYPE
// EXTRA_ARGS_DEC
// EXTRA_ARGS

__kernel void
pyscical_ode_solver_iter1(T_TYPE t, T_TYPE h, const __global Y_TYPE *y_in,
                          __global Y_TYPE *k1, __global Y_TYPE *y_next,
                          ulong n EXTRA_ARGS_DEC)
{
    const T_TYPE h_3 = h / 3;
    const size_t gsize = get_global_size(0);
    size_t i = get_global_id(0);
    for (;i < n;i += gsize) {
        const Y_TYPE y_in_i = y_in[i];
        Y_TYPE k = elwise_diff_func(t, y_in, i, y_in_i EXTRA_ARGS);
        k1[i] = k;
        y_next[i] = y_in_i + h_3 * k;
    }
}

__kernel void
pyscical_ode_solver_iter2(T_TYPE t, T_TYPE h, const __global Y_TYPE *y_in,
                          const __global Y_TYPE *k1, __global Y_TYPE *k2,
                          __global Y_TYPE *y_next, ulong n EXTRA_ARGS_DEC)
{
    const T_TYPE h_3 = h / 3;
    const T_TYPE t2 = t + h_3;
    const size_t gsize = get_global_size(0);
    size_t i = get_global_id(0);
    for (;i < n;i += gsize) {
        const Y_TYPE y_in_i = y_in[i];
        Y_TYPE k = elwise_diff_func(t2, y_in, i, y_in_i EXTRA_ARGS);
        k2[i] = k;
        y_next[i] = y_in_i + h * ((-2 / 3.0) * k1[i] + k);
    }
}

__kernel void
pyscical_ode_solver_iter3(T_TYPE t, T_TYPE h, const __global Y_TYPE *y_in,
                          const __global Y_TYPE *k1, const __global Y_TYPE *k2,
                          __global Y_TYPE *k3, __global Y_TYPE *y_next,
                          ulong n EXTRA_ARGS_DEC)
{
    const T_TYPE h2_3 = (2.0 / 3) * h;
    const T_TYPE t3 = t + h2_3;
    const size_t gsize = get_global_size(0);
    size_t i = get_global_id(0);
    for (;i < n;i += gsize) {
        const Y_TYPE y_in_i = y_in[i];
        Y_TYPE k = elwise_diff_func(t3, y_in, i, y_in_i EXTRA_ARGS);
        k3[i] = k;
        y_next[i] = y_in_i + h * (k1[i] * (4.0 / 3) - k2[i] * 2 + k);
    }
}

__kernel void
pyscical_ode_solver_iter4(T_TYPE t, T_TYPE h, const __global Y_TYPE *y_in,
                          const __global Y_TYPE *k1, const __global Y_TYPE *k2,
                          const __global Y_TYPE *k3, __global Y_TYPE *y_next,
                          ulong n EXTRA_ARGS_DEC)
{
    const T_TYPE t4 = t + h;
    const T_TYPE h_8 = (1.0 / 8) * h;
    const size_t gsize = get_global_size(0);
    size_t i = get_global_id(0);
    for (;i < n;i += gsize) {
        const Y_TYPE y_in_i = y_in[i];
        Y_TYPE k = elwise_diff_func(t4, y_in, i, y_in_i EXTRA_ARGS);
        y_next[i] = y_in_i + h_8 * (k - 5 * k3[i] + 11 * k2[i] - 7 * k1[i]);
    }
}
