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

__all__ = ['compose_g', 'compose_gJ', 'compose_gF', 'sideband_strength',
           'sideband_scatter_strength', 'Transition']

from .constants import *
import sys
from ._cffi import _ffi, _lib
from optics import Focus


def compose_g(J_sum, J1, J2, g1, g2):
    if not J_sum:
        return 0.0
    J_sum_2 = J_sum * (J_sum + 1)
    J1_2 = J1 * (J1 + 1)
    J2_2 = J2 * (J2 + 1)
    return (g1 * (J_sum_2 + J1_2 - J2_2) +
            g2 * (J_sum_2 + J2_2 - J1_2)) / 2 / J_sum_2


def compose_gJ(J, L, S):
    return compose_g(J, L, S, 1.0, g_e)


def compose_gF(F, I, J, L, S, g_I=0.0):
    return compose_g(F, I, J, g_I, compose_gJ(J, L, S))


def sideband_strength(n1, n2, eta):
    # change this to float128 after pypy support it
    return float(_lib.harmonic_recoil(n1, n2, eta))


def sideband_scatter_strength(n1, n2, eta, theta0):
    # change this to float128 after pypy support it
    return float(_lib.harmonic_scatter(n1, n2, eta, theta0))


class Transition(object):
    def __init__(self, **kws):
        if 'freq' in kws:
            self.__freq = kws.pop('freq')
        elif 'lamb' in kws:
            self.__freq = c_0 / kws.pop('lamb')
        else:
            raise TypeError('no arguments to initialize frequency')
        if 'dipole' in kws:
            self.__dipole = kws.pop('dipole')
        else:
            raise TypeError('no arguments to initialize dipole moment')
        if kws:
            raise TypeError('too many arguments to initialize Transition')

    @property
    def omega(self):
        return self.freq * 2 * pi

    @property
    def freq(self):
        return self.__freq

    @property
    def lamb(self):
        return c_0 / self.__freq

    @property
    def dipole(self):
        return self.__dipole

    def ac_stark(self, freq, I=1):
        return -(self.__dipole**2 * I / hbar / c_0 / epsilon_0 / 4 / pi
                 * (1 / (self.__freq - freq) + 1 / (self.__freq + freq)))


class ODT(Focus):
    def __init__(self, transitions, power, mass, **kws):
        Focus.__init__(self, **kws)
        self.__trans = tuple(transitions)
        self.__P = power
        self.__m = mass

    def __ac_stark(self, I=1):
        return -sum(t.ac_stark(self.freq, I) for t in self.__trans)

    @property
    def freq(self):
        return c_0 / self.lamb

    @property
    def power(self):
        return self.__P

    @property
    def focus_I(self):
        return Focus.focus_I(self, self.__P)

    @property
    def depth(self):
        return self.__ac_stark(self.focus_I)

    @property
    def depth_f(self):
        return self.depth / h

    @property
    def depth_omega(self):
        return self.depth / hbar

    @property
    def trap_omega_l(self):
        return 2 / self.radius_l * sqrt(self.depth / self.__m)

    @property
    def trap_omega_r(self):
        return 2 / self.radius_r * sqrt(self.depth / self.__m)

    @property
    def trap_freq_l(self):
        return self.trap_omega_l / 2 / pi

    @property
    def trap_freq_r(self):
        return self.trap_omega_r / 2 / pi

    @property
    def z0_l(self):
        return sqrt(hbar / 2 / self.__m / self.trap_omega_l)

    @property
    def z0_r(self):
        return sqrt(hbar / 2 / self.__m / self.trap_omega_r)

    def eta_l(self, lamb):
        return 2 * pi / lamb * self.z0_l

    def eta_r(self, lamb):
        return 2 * pi / lamb * self.z0_r

    @property
    def nmax_r(self):
        return self.depth_f / self.trap_freq_r / 2

    @property
    def nmax_l(self):
        return self.depth_f / self.trap_freq_l / 2


# pure python version is faster than cffi wrapper on pypy
if '__pypy__' not in sys.modules:
    compose_g = _lib.compose_g
    compose_gJ = _lib.compose_gJ

    def compose_gF(F, I, J, L, S, g_I=0.0):
        return _lib.compose_gF(F, I, J, L, S, g_I)
