# Copyright 2012 Yu Yichao
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

from .constants import *
from .constants import _reg, _constants
import sys

_module = sys.modules[__name__]
def _def_scaled_units(baseval, basesym, basename):
    _prefixes = (('Y', 'yotta', 1e24),
                ('Z', 'zetta', 1e21),
                ('E', 'exa', 1e18),
                ('P', 'peta', 1e15),
                ('T', 'tera', 1e12),
                ('G', 'giga', 1e9),
                ('M', 'mega', 1e6),
                ('k', 'kilo', 1e3),
                ('h', 'hecto', 1e2),
                ('D', 'deka', 1e1),
                ('', '', 1),
                ('d', 'deci', 1e-1),
                ('c', 'centi', 1e-2),
                ('m', 'milli', 1e-3),
                ('u', 'micro', 1e-6),
                ('n', 'nano', 1e-9),
                ('p', 'pico', 1e-12),
                ('f', 'femto', 1e-15),
                ('a', 'atto', 1e-18),
                ('z', 'zepto', 1e-21))
    for presym, prename, preval in _prefixes:
        if basesym:
            sym = presym + basesym
        elif prename:
            sym = prename
        else:
            continue
        if not (basesym or presym):
            continue
        if not prename:
            name = basename
        elif not basename:
            name = prename
        else:
            name = ' '.join((prename, basename))
        setattr(_module, sym, _reg(preval * baseval, name))

_def_scaled_units(1, '', '')

_def_scaled_units(e_0, 'eV', 'electron volt')
_def_scaled_units(e_0 / c**2, 'eVm', 'electron volt mass')
_def_scaled_units(e_0 / h, 'eVf', 'electron volt frequency')
_def_scaled_units(e_0 / k_B, 'eVT', 'electron volt temperature')

_def_scaled_units(1, 'Hz', 'Hertz')
_def_scaled_units(h / k_B, 'HzT', 'Hertz temperature')
_def_scaled_units(h / c**2, 'Hzm', 'Hertz mass')

_def_scaled_units(1, 'K', 'Kelvin')
_def_scaled_units(k_B / h, 'Kf', 'Kelvin frequency')

_def_scaled_units(1, 'm', 'meter')
_def_scaled_units(1, 's', 'second')
_def_scaled_units(1e-3, 'g', 'gram')
_def_scaled_units(1, 'Pa', 'Pascal')
_def_scaled_units(1e-3, 'L', 'liter')

D = _reg(1e-21 / c, 'Debye')

ft = foot = _reg(0.3048, 'foot')
inch = _reg(25.4e-3, 'inch')
yd = yard = _reg(3 * ft, 'yard')
mile = _reg(5280 * ft, 'mile')

minute = _reg(60, 'minute')
hour = _reg(3600, 'hour')
day = _reg(24 * hour, 'day')
week = _reg(7 * day, 'week')
month = _reg(30 * day, 'month')
yr = year = _reg(365 * day, 'year')
Julian_year = _reg(_constants.Julian_year, 'Julian year')

bar = _reg(1e5, 'bar')
pound = _reg(0.45359237, 'pound')
psi = _reg(pound / inch ** 2, 'pound per square inche')

torr = mmHg = _reg(13.5951 * g_0, 'millimeter mercury pressure')

ly = light_year = _reg(c * year, 'light year')
