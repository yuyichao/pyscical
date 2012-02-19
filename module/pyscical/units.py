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

from .phyconsts import c, eV

km = 1e3
dm = 1e-1
cm = 1e-2
mm = 1e-3
um = 1e-6
nm = 1e-9
pm = 1e-12
fm = 1e-15

ft = foot = 0.3048
inch = 25.4 * mm
yd = yard = 3 * ft
mile = 5280 * ft

L = liter = 1e-3
dL = 1e-4
cL = 1e-5
mL = 1e-6

# Common time units

ms = 1e-3
us = 1e-6
ns = 1e-9
ps = 1e-12

minute = 60
hour = 3600
day = 24 * hour

a = year = 365 * day

g = 1e-3
mg = 1e-6
ug = 1e-9

kPa = 1e3
bar = 1e5
pound = 0.45359237
psi = pound / inch ** 2

dHg0 = 13.5951
mmHg = dHg0 * 9.80665
quart = 231 * inch**3

ly = lightyear = c * year
