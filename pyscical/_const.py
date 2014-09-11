#!/usr/bin/env python
#
# Copyright (C) 2012~2014 by Yichao Yu
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

from numpy import pi

e = 1.602176565e-19
h = 6.62606957e-34
hbar = h / 2 / pi
G = 6.67384e-11
g = 9.80665
R = 8.3144621
alpha = 0.0072973525698
N_A = 6.02214129e+23
k = 1.3806488e-23
sigma = 5.670373e-08
Wien = 0.0028977721
Rydberg = 10973731.568539
m_e = 9.10938291e-31
m_n = 1.672621777e-27
m_p = 1.674927351e-27

_values = {
    'electron g factor': 2.00231930436153,
    'neutron g factor': -3.82608545,
    'proton g factor': 5.585694713
    }


def value(name):
    return _values[name]

Julian_year = 31557600.0
