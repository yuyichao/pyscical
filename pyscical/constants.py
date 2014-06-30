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

from math import *
from math import e as E
try:
    from scipy import constants as _constants
except ImportError:
    from . import _const as _constants
from .value import Value


class Constants(dict):
    def _reg(self, val, name):
        val = Value(val, name)
        self[name] = val
        return val

Constants = Constants()
_reg = Constants._reg

c = _reg(299792458, 'speed of light in vaccum')
c_0 = c
mu_0 = _reg(4 * pi * 1e-7, 'vacuum permeability')
epsilon_0 = _reg(1 / mu_0 / c**2, 'vacuum permittivity')
h = _reg(_constants.h, 'Planck constant')
hbar = _reg(_constants.hbar, 'reduced Planck constant')
G_N = _reg(_constants.G, 'gravitational constant')
g_0 = _reg(_constants.g, 'standard gravity')
E = _reg(E, 'Napier constant')
e = _reg(_constants.e, 'elementary charge')
e_0 = e
R_g = _reg(_constants.R, 'molar gas constant')
alpha = _reg(_constants.alpha, 'fine-structure constant')
N_A = _reg(_constants.N_A, 'Avogadro constant')
k_B = _reg(_constants.k, 'Boltzmann constant')
sigma = _reg(_constants.sigma, 'Stefan-Boltzmann constant')
b_wien = _reg(_constants.Wien, 'Wien displacement law constant')
R_inf = _reg(_constants.Rydberg, 'Rydberg constant')
m_e = _reg(_constants.m_e, 'electron mass')
m_p = _reg(_constants.m_n, 'proton mass')
m_n = _reg(_constants.m_p, 'neutron mass')

Z_0 = _reg(mu_0 * c, 'characteristic impedance of vacuum')
k_e = _reg(1 / (4 * pi * epsilon_0), 'Coulomb constant')
G_0 = _reg(2 * e**2 / h, 'Conductance quantum')

l_P = _reg(hbar * G_N / c**3, 'Planck length')
m_P = _reg(sqrt(hbar * c / G_N), 'Planck mass')
E_P = _reg(m_P * c**2, 'Planck energy')
t_P = _reg(l_P / c, 'Planck time')
q_P = _reg(sqrt(4 * pi * epsilon_0 * hbar * c), 'Planck charge')
T_P = _reg(E_P / k_B, 'Planck temperature')

K_J = _reg(2 * e / h, 'Josephson constant')
R_K = _reg(h / e**2, 'von Klitzing constant')
phi_0 = _reg(h / (2 * e), 'magnetic flux quantum')
F_c = _reg(N_A * e, 'Faraday constant')

mu_B = _reg(e * hbar / (2 * m_e), 'Bohr magneton')
mu_N = _reg(e * hbar / (2 * m_p), 'nuclear magneton')
mu_Bf = _reg(mu_B / h, 'Bohr magneton frequency')
mu_Nf = _reg(mu_B / h, 'nuclear magneton frequency')

a_0 = _reg(alpha / (4 * pi * R_inf), 'Bohr radius')
r_e = _reg(e**2 / (4 * pi * epsilon_0 * m_e * c**2),
           'classical electron radius')
E_h = _reg(2 * R_inf * h * c, 'hartree')

g_e = _reg(abs(_constants.value('electron g factor')), 'electron g factor')
g_n = _reg(_constants.value('neutron g factor'), 'neutron g factor')
g_p = _reg(_constants.value('proton g factor'), 'proton g factor')
