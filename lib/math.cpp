/* Copyright (C) 2014~2014 by Yichao Yu
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

#include "pyscical.h"

#include <tr1/cmath>
#include <array>
#include <iostream>
#include <atomic>

PYSCICAL_EXPORT long double
genlaguerre(unsigned n, unsigned m, long double x)
{
    return std::tr1::assoc_laguerre(n, m, x);
}

static PYSCICAL_INLINE long double
_lfactorial(unsigned n)
{
    static constexpr size_t cache_size = 1024;
    static long double cache[cache_size] = {0};
    if (n < cache_size) {
        if (cache[n] != 0) {
            return cache[n];
        } else {
            cache[n] = std::lgamma((long double)(n + 1));
            return cache[n];
        }
    }
    return std::lgamma((long double)(n + 1));
}

PYSCICAL_EXPORT long double
harmonic_recoil(unsigned n1, unsigned n2, long double eta)
{
    unsigned nl;
    unsigned ng;
    if (n1 > n2) {
        ng = n1;
        nl = n2;
    } else  {
        ng = n2;
        nl = n1;
    }
    unsigned dn = ng - nl;
    if (eta == 0) {
        return dn == 0 ? 1 : 0;
    }
    auto eta2 = eta * eta;
    auto lpre = ((-eta2 + _lfactorial(nl) - _lfactorial(ng)) / 2
                 + std::log(eta) * dn);
    auto lag = std::tr1::assoc_laguerre(nl, dn, eta2);
    return static_cast<double>(lag * std::exp(lpre));
}

static constexpr unsigned _theta_n = 21;
typedef std::array<long double, _theta_n> theta_ary_t;

static PYSCICAL_INLINE theta_ary_t
make_thetas()
{
    theta_ary_t ary;
    for (unsigned i = 0;i < _theta_n;i++) {
        ary[i] = -M_PI_2l / 2 + M_PIl / (_theta_n - 1) * i;
    }
    return ary;
}

static PYSCICAL_INLINE theta_ary_t
sin_array(theta_ary_t ary_in)
{
    theta_ary_t ary_out;
    for (unsigned i = 0;i < _theta_n;i++) {
        ary_out[i] = sin(ary_in[i]);
    }
    return ary_out;
}

static PYSCICAL_INLINE theta_ary_t
cos_array(theta_ary_t ary_in)
{
    theta_ary_t ary_out;
    for (unsigned i = 0;i < _theta_n;i++) {
        ary_out[i] = cos(ary_in[i]);
    }
    return ary_out;
}

static PYSCICAL_INLINE long double
sum_array(theta_ary_t ary)
{
    long double s = 0;
    for (auto &ele: ary) {
        s += ele;
    }
    return s;
}

const static theta_ary_t thetas = make_thetas();
const static theta_ary_t sin_thetas = sin_array(thetas);
const static theta_ary_t cos_thetas = cos_array(thetas);
const static long double sum_cos_thetas = sum_array(cos_thetas);

PYSCICAL_EXPORT long double
harmonic_scatter(unsigned n1, unsigned n2, long double eta, long double theta0)
{
    long double strengths[_theta_n];
    long double s0 = sin(theta0);
#pragma omp parallel for
    for (unsigned i = 0;i < _theta_n;i++) {
        long double strength =
            harmonic_recoil(n1, n2, eta * std::abs(sin_thetas[i] - s0));
        strengths[i] = strength * strength * cos_thetas[i];
    }
    long double sum = 0;
    for (unsigned i = 0;i < _theta_n;i++) {
        sum += strengths[i];
    }
    return sum / sum_cos_thetas;
}
