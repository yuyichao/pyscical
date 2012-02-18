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

Z_0 = mu_0 * c
k_e = 1 / (4 * pi * epsilon_0)
G_0 = 2 * e**2 / h
K_J = 2 * e / h
phi_0 = h / (2 * e)
R_K = h / e**2
F_c = N_A * e

# The original name might easily be overrided.
G_N = G
k_B = k
R_g = R
g_n = g

l_P = sqrt(hbar * G_N / c**3)
m_P = sqrt(hbar * c / G_N)
E_P = m_P * c**2
t_P = l_P / c
q_P = sqrt(4 * pi * epsilon_0 * hbar * c)
T_P = E_P / k_B

keV = kilo * eV
MeV = mega * eV
GeV = giga * eV
TeV = tera * eV
eVm = eV / c**2 # mass for 1eV
keVm = kilo * eVm
MeVm = mega * eVm
GeVm = giga * eVm
TeVm = tera * eVm

mu_B = e * hbar / (2 * m_e)
mu_N = e * hbar / (2 * m_p)
R_inf = Rydberg
a0 = alpha / (4 * pi * R_inf)
r_e = e**2 / (4 * pi * epsilon_0 * m_e * c**2)
E_h = 2 * R_inf * h * c


M_sun = 1.9891e30
R_sun = 6.955e8
M_earth = 5.9736e24
R_earth = 6371.0e3

# for chem maybe
atom_m = {
    'H': 1.00794, #average
    'H1': 1.00782503207,
    'H2': 2.0141017779,
    'D': 2.0141017779,
    'H3': 3.0160492777,
    'T': 3.0160492777,
    'He': 4.002602,
    'Li': 6.941,
    'Be': 9.012182,
    'B': 10.811,
    'C': 12.011,
    'N': 14.00674,
    'O': 15.9994,
    'F': 18.9984,
    'Ne': 20.1797,
    'Na': 22.98977,
    'Mg': 24.305,
    'Al': 26.98154,
    'Si': 28.0855,
    'P': 30.97376,
    'S': 32.066,
    'Cl': 35.4527,
    'K': 39.0983,
    'Ar': 39.948,
    'Ca': 40.078,
    'Sc': 44.95591,
    'Ti': 47.88,
    'V': 50.9415,
    'Cr': 51.9961,
    'Mn': 54.93805,
    'Fe': 55.847,
    'Ni': 58.6934,
    'Co': 58.9332,
    'Cu': 63.546,
    'Zn': 65.39,
    'Ga': 69.723,
    'Ge': 72.61,
    'As': 74.92159,
    'Se': 78.96,
    'Br': 79.904,
    'Kr': 83.8,
    'Rb': 85.4678,
    'Sr': 87.62,
    'Y': 88.90585,
    'Zr': 91.224,
    'Nb': 92.90638,
    'Mo': 95.94,
    'Tc': 98,
    'Ru': 101.07,
    'Rh': 102.9055,
    'Pd': 106.42,
    'Ag': 107.8682,
    'Cd': 112.411,
    'In': 114.818,
    'Sn': 118.71,
    'Sb': 121.757,
    'I': 126.9045,
    'Te': 127.6,
    'Xe': 131.29,
    'Cs': 132.9054,
    'Ba': 137.327,
    'La': 138.9055,
    'Ce': 140.115,
    'Pr': 140.9077,
    'Nd': 144.24,
    'Pm': 145,
    'Sm': 150.36,
    'Eu': 151.965,
    'Gd': 157.25,
    'Tb': 158.9253,
    'Dy': 162.5,
    'Ho': 164.9303,
    'Er': 167.26,
    'Tm': 168.9342,
    'Yb': 173.04,
    'Lu': 174.967,
    'Hf': 178.49,
    'Ta': 180.9479,
    'W': 183.85,
    'Re': 186.207,
    'Os': 190.2,
    'Ir': 192.22,
    'Pt': 195.08,
    'Au': 196.9665,
    'Hg': 200.59,
    'Tl': 204.3833,
    'Pb': 207.2,
    'Bi': 208.9804,
    'Po': 208.9824,
    'At': 209.9871,
    'Pa': 213.0359,
    'Rn': 222,
    'Fr': 223,
    'Ra': 226.0254,
    'Ac': 227.0728,
    'Th': 232.0381,
    'Np': 237.0482,
    'U': 238.0289,
    'Am': 243.0614,
    'Pu': 244.0642,
    'Cm': 247,
    'Bk': 247,
    'Cf': 251,
    'Es': 252,
    'Fm': 257,
    'Md': 258,
    'No': 259,
    'Lr': 260,
    'Rf': 261,
    'Db': 262,
    'Bh': 262,
    'Sg': 263,
    'Hs': 265,
    'Mt': 266,
    'Ds': 271,
    'Rg': 272
}

# del to clean up auto completion in ipython
del atomic_mass
del gravitational_constant
del Boltzmann
del Stefan_Boltzmann
del Avogadro
del ConstantWarning
