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

static const double g_e = 2.00231930436153;

PYSCICAL_EXPORT double
compose_g(double J_sum, double J1, double J2, double g1, double g2)
{
    if (!J_sum)
        return 0;
    double J_sum_2 = J_sum * (J_sum + 1);
    double J1_2 = J1 * (J1 + 1);
    double J2_2 = J2 * (J2 + 1);
    return (g1 * (J_sum_2 + J1_2 - J2_2) +
            g2 * (J_sum_2 + J2_2 - J1_2)) / 2 / J_sum_2;
}

PYSCICAL_EXPORT double
compose_gJ(double J, double L, double S)
{
    return compose_g(J, L, S, 1.0, g_e);
}

PYSCICAL_EXPORT double
compose_gF(double F, double I, double J, double L, double S, double g_I)
{
    return compose_g(F, I, J, g_I, compose_gJ(J, L, S));
}
