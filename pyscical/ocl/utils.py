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

import pyopencl as cl
from os import path as _path

src_dir = _path.dirname(_path.abspath(__file__))


class CLArg(object):
    __slots__ = ('__name', '__ctype', '__decl', '__convert')

    def __init__(self, name, ctype, decl=None, convert=None):
        self.__name = name
        self.__ctype = ctype
        self.__decl = decl if decl else (ctype + ' ' + name)
        self.__convert = convert

    @property
    def name(self):
        return self.__name

    @property
    def ctype(self):
        return self.__ctype

    @property
    def decl(self):
        return self.__decl

    @property
    def convert(self):
        return self.__convert


def get_group_sizes(n, dev, kernel=None):
    max_work_items = dev.max_work_group_size
    if kernel is not None:
        max_work_items = min(
            max_work_items, kernel.get_work_group_info(
                cl.kernel_work_group_info.WORK_GROUP_SIZE, dev))
    min_work_items = min(32, max_work_items)
    max_groups = dev.max_compute_units * 4 * 8
    # 4 to overfill the device
    # 8 is an Nvidia constant--that's how many
    # groups fit onto one compute device

    if n < min_work_items:
        group_count = 1
        work_items_per_group = min_work_items
    elif n < (max_groups * min_work_items):
        group_count = (n + min_work_items - 1) // min_work_items
        work_items_per_group = min_work_items
    elif n < (max_groups * max_work_items):
        group_count = max_groups
        grp = (n + min_work_items - 1) // min_work_items
        work_items_per_group = (
            (grp + max_groups - 1) // max_groups) * min_work_items
    else:
        group_count = max_groups
        work_items_per_group = max_work_items

    return (group_count * work_items_per_group,), (work_items_per_group,)
