# Find Python
# ~~~~~~~~~~~
# Find the Python interpreter and related Python directories.
#
# This file defines the following variables:
#
# PYTHON_EXECUTABLE
#     The path and filename of the Python interpreter.
#
# PYTHON_SHORT_VERSION
#     The version of the Python interpreter found,
#     excluding the patch version number. (e.g. 2.5 and not 2.5.1))
#
# PYTHON_LONG_VERSION
#     The version of the Python interpreter found as a human readable string.
#
# PYTHON_SITE_PACKAGES_INSTALL_DIR
#     This cache variable can be used for installing own python modules.
#     You may want to adjust this to be the same as
#     ${PYTHON_SITE_PACKAGES_DIR}, but then admin privileges may be required
#     for installation.
#
# PYTHON_SITE_PACKAGES_DIR
#     Location of the Python site-packages directory.
#
# PYTHON_INCLUDE_PATH
#     Directory holding the python.h include file.
#
# PYTHON_MAGIC_TAG
#     The magic tag used in byte compiling (PEP 3147)

#   Copyright (C) 2012~2012 by Yichao Yu
#   yyc1992@gmail.com
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, version 2 of the License.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the
#   Free Software Foundation, Inc.,
#   59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.

# This file incorporates work covered by the following copyright and
# permission notice:
#
#     Copyright (c) 2007, Simon Edwards <simon@simonzone.com>
#     Redistribution and use is allowed according to the terms of the BSD
#     license. For details see the accompanying COPYING-CMAKE-SCRIPTS file.

include(CMakeFindFrameworks)

find_package(PythonInterp)
# get the directory of the current file, used later on in the file
get_filename_component(_py_cmake_module_dir ${CMAKE_CURRENT_LIST_FILE} PATH)
set(_cmake_python_helper "${_py_cmake_module_dir}/cmake-python-helper.py")
if(NOT EXISTS "${_cmake_python_helper}")
  message(FATAL_ERROR "The file cmake-python-helper.py does not exist in ${_py_cmake_module_dir} (the directory where FindPythonLibrary.cmake is located). Check your installation.")
endif()

if(PYTHONINTERP_FOUND)
  execute_process(COMMAND ${PYTHON_EXECUTABLE}
    "${_cmake_python_helper}" --get-sys-info OUTPUT_VARIABLE python_config)
  if(python_config)
    string(REGEX REPLACE ".*exec_prefix:([^\n]+).*$" "\\1"
      PYTHON_PREFIX ${python_config})
    string(REGEX REPLACE ".*\nshort_version:([^\n]+).*$" "\\1"
      PYTHON_SHORT_VERSION ${python_config})
    string(REGEX REPLACE ".*\nlong_version:([^\n]+).*$" "\\1"
      PYTHON_LONG_VERSION ${python_config})
    string(REGEX REPLACE ".*\npy_inc_dir:([^\n]+).*$" "\\1"
      _TMP_PYTHON_INCLUDE_PATH ${python_config})
    string(REGEX REPLACE ".*\nsite_packages_dir:([^\n]+).*$" "\\1"
      _TMP_PYTHON_SITE_PACKAGES_DIR ${python_config})
    string(REGEX REPLACE ".*\nmagic_tag:([^\n]*).*$" "\\1"
      PYTHON_MAGIC_TAG ${python_config})

    # Put these two variables in the cache so they are visible for the user, but read-only:
    set(PYTHON_INCLUDE_PATH "${_TMP_PYTHON_INCLUDE_PATH}"
      CACHE PATH "The python include directory" FORCE)
    set(PYTHON_SITE_PACKAGES_DIR "${_TMP_PYTHON_SITE_PACKAGES_DIR}"
      CACHE PATH "The python site packages dir" FORCE)

    # This one is intended to be used and changed by the user for
    # installing own modules:
    if(NOT PYTHON_SITE_PACKAGES_INSTALL_DIR)
      set(PYTHON_SITE_PACKAGES_INSTALL_DIR ${_TMP_PYTHON_SITE_PACKAGES_DIR})
    endif()

    string(REGEX REPLACE "([0-9]+).([0-9]+)" "\\1\\2"
      PYTHON_SHORT_VERSION_NO_DOT ${PYTHON_SHORT_VERSION})
  endif()
endif()

if(NOT PYTHONLIBRARY_FIND_QUIETLY)
  message(STATUS "Found Python executable: ${PYTHON_EXECUTABLE}")
  message(STATUS "Found Python version: ${PYTHON_LONG_VERSION}")
endif()
