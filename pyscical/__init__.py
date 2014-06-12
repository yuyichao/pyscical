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

try:
    # Detect whether we are in IPython. This works because `get_ipython` is
    # added to __builtins__
    get_ipython
except NameError:
    pass
else:
    from ._ipython import *

from ._general import *
from .constants import *
from .units import *
from .astro import *
from . import atom_mass as at_m
from . import atomic
