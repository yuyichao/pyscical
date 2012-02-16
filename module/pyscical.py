#!/usr/bin/env python

# Copyright 2011 Yu Yichao
# yyc1992@gmail.com
#
# This file is part of PySciCal.
#
# PySciCal is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PySciCal is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with PySciCal.  If not, see <http://www.gnu.org/licenses/>.

from math import *
from math import e as E
from numpy import *
from pylab import *
from scipy.constants import *

G_N = G
Z_0 = mu_0 * c
k_e = 1 / (4 * pi * epsilon_0)
G_0 = 2 * e**2 / h
K_J = 2 * e / h
phi_0 = h / (2 * e)
R_K = h / e**2
k_B = k
F = N_A * e

l_P = sqrt(hbar * G / c**3)
m_P = sqrt(hbar * c / G)
E_P = m_P * c**2
t_P = l_P / c
q_P = sqrt(4 * pi * epsilon0 * hbar * c)
T_P = E_P / k_B

keV = 1e3 * eV
MeV = 1e6 * eV
GeV = 1e9 * eV
TeV = 1e12 * eV
eVm = eV / c**2 # mass for 1eV
keVm = 1e3 * eVm
MeVm = 1e6 * eVm
GeVm = 1e9 * eVm
TeVm = 1e12 * eVm

mu_B = e * hbar / (2 * m_e)
mu_N = e * hbar / (2 * m_p)
R_inf = Rydberg
a0 = alpha / (4 * pi * R_inf)
r_e = e**2 / (4 * pi * epsilon0 * m_e * c**2)
E_h = 2 * R_inf * h * c

g_n = g

# for chem maybe
atom_m = {
    'H1': 1.00782503207,
    'H2': 2.0141017779,
    'D': 2.0141017779,
    'H3': 3.0160492777,
    'T': 3.0160492777
}
