#!/usr/bin/env python
#
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

from numpy import floor, log10
import six

__all__ = ['format_unc']


def _format_unc(a, s, unit, sci, tex):
    '''input: observable, error
       output: formatted observable +- error in scientific notation'''
    if s <= 0:
        return '%f%s' % (a, unit)

    if sci is None:
        sci = (s >= 100) or max(abs(a), s) < .1

    la = int(floor(log10(abs(a))))
    ls = int(floor(log10(s)))
    fs = floor(s * 10**(1 - ls))
    if sci:
        fa = a * 10**-la
        dl = la - ls + 1
    else:
        fa = a
        dl = 1 - ls
    dl = dl if dl > 0 else 0

    if dl == 1:
        ss = '%.1f' % (fs / 10)
    else:
        ss = '%.0f' % fs

    if sci:
        if tex:
            return (('%.' + ('%d' % dl) + r'f(%s)\times10^{%d}{%s}') %
                    (fa, ss, la, unit))
        else:
            return ('%.' + ('%d' % dl) + 'f(%s)*10^%d%s') % (fa, ss, la, unit)
    else:
        return ('%.' + ('%d' % dl) + 'f(%s)%s') % (fa, ss, unit)


def _get_if_list(lst, idx, _def):
    if isinstance(lst, six.string_types):
        return lst
    try:
        return lst[idx]
    except IndexError:
        return _def
    except:
        return lst


def format_unc(vals, uncs, unit='', sci=None, tex=False):
    try:
        it = enumerate(vals)
    except TypeError:
        return _format_unc(vals, _get_if_list(uncs, 0, 0),
                           _get_if_list(unit, 0, ''),
                           _get_if_list(sci, 0, None),
                           _get_if_list(tex, 0, False))
    return [_format_unc(v, _get_if_list(uncs, i, 0), _get_if_list(unit, i, ''),
                        _get_if_list(sci, i, None),
                        _get_if_list(tex, i, False)) for (v, i) in it]
