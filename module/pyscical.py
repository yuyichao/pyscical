#!/usr/bin/env python

from math import *
from numpy import *
from pylab import *

c = 299792458
G_N = 6.67384e-11
h = 6.62606957e-34
hbar = h / 2 / pi
mu0 = 4e-7 * pi
epsilon0 = 1 / (mu0 * c**2)
Z0 = mu0 * c
k_e = 1 / (4 * pi * epsilon0)
e, E = 1.602176565e-19, e # e is defined in math
G0 = 2 * e**2 / h
K_J = 2 * e / h
phi0 = h / (2 * e)
R_K = h / e**2
alpha = e**2 / (4 * pi * epsilon0 * hbar * c)
N_A = 6.02214129e23
m_u = 1.660538921e-27
k_B = 1.3806488e-23
R = N_A * k_B
F = N_A * e

l_P = sqrt(hbar * G_N / c**3)
m_P = sqrt(hbar * c / G_N)
E_P = m_P * c**2
t_P = l_P / c
q_P = sqrt(4 * pi * epsilon0 * hbar * c)
T_P = E_P / k_B

eV = e
keV = 1e3 * eV
MeV = 1e6 * eV
GeV = 1e9 * eV
TeV = 1e12 * eV
eVm = eV / c**2 # mass for 1eV
keVm = 1e3 * eVm
MeVm = 1e6 * eVm
GeVm = 1e9 * eVm
TeVm = 1e12 * eVm
atm = 101325

m_e = 9.10938291e-31
m_p = 1.672621777e-27
mu_B = e * hbar / (2 * m_e)
mu_N = e * hbar / (2 * m_p)
R_inf = alpha**2 * m_e * c / (2 * h)
a0 = alpha / (4 * pi * R_inf)
r_e = e**2 / (4 * pi * epsilon0 * m_e * c**2)
E_h = 2 * R_inf * h * c

g_n = 9.80665

# for chem maybe
atom_m = {
    'H1': 1.00782503207,
    'H2': 2.0141017779,
    'D': 2.0141017779,
    'H3': 3.0160492777,
    'T': 3.0160492777
}
