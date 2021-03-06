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

from numpy import *

__all__ = ['Focus']


class Focus(object):
    """
    The focus of a light beam.
    """
    __slots__ = ['__fnum', '__lamb']

    def __init_theta(self, sin_t):
        self.__fnum = sqrt(1 / sin_t**2 - 1)

    def __init__(self, lamb=None, **kws):
        self.__lamb = lamb
        if 'fnum' in kws:
            self.__fnum = kws.pop('fnum')
        elif 'NA' in kws:
            sin_t = kws.pop('NA') / kws.pop('n', 1)
            self.__init_theta(sin_t)
        elif 'theta' in kws:
            self.__init_theta(sin(kws.pop('theta')))
        else:
            raise TypeError('no arguments to initialize Focus')
        if kws:
            raise TypeError('too many arguments to initialize Focus')

    def focus_I(self, P):
        """Intensity at the center of the focus with power P."""
        return P * pi / (self.__lamb * self.__fnum)**2

    @property
    def quad_r(self):
        # Comes from the expension of (2 * J_1(v) / v)**2
        # where v = 2 * pi / lambda / f# * r
        return (pi / self.__lamb / self.__fnum)**2

    @property
    def quad_l(self):
        # Comes from the expension of (sin(u / 4) / (u / 4))**2
        # where u = 2 * pi / lambda / f#**2 * z
        return (pi / self.__lamb / self.__fnum**2)**2 / 12

    @property
    def radius_r(self):
        return sqrt(2) * self.__lamb * self.__fnum / pi

    @property
    def radius_l(self):
        return 2 * sqrt(6) * self.__lamb * self.__fnum**2 / pi

    @property
    def lamb(self):
        return self.__lamb

    @property
    def fnum(self):
        return self.__fnum
