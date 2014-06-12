project(QtCurve)

## Setup
cmake_minimum_required(VERSION 2.8)
set(CMAKE_MODULE_PATH "${CMAKE_MODULE_PATH}"
  "${CMAKE_CURRENT_SOURCE_DIR}/cmake")

include(PythonMacros)
include(CMakeCMacros)

# ## Version
# set(PYSCICAL_VERSION_MAJOR "0")
# set(PYSCICAL_VERSION_MINOR "1")
# set(PYSCICAL_VERSION_PATCH "0")
# set(PYSCICAL_VERSION "${PYSCICAL_VERSION_MAJOR}.${PYSCICAL_VERSION_MINOR}")
# set(PYSCICAL_VERSION_FULL "${PYSCICAL_VERSION}.${PYSCICAL_VERSION_PATCH}")

if(NOT BIN_DIR)
  set(BIN_DIR bin)
endif()

cmake_c_add_flags(CMAKE_C_FLAGS -Wall -Wextra -std=gnu99)
# -std=c++0x is deprecated but gcc < 4.7 do not recognise c++11 ....
cmake_c_add_flags(CMAKE_CXX_FLAGS -Wall -Wextra
  -Wno-deprecated-register -std=c++0x)
cmake_c_add_flags(CMAKE_SHARED_LINKER_FLAGS -Wl,--as-needed -Wl,--no-undefined)
cmake_c_add_flags(CMAKE_MODULE_LINKER_FLAGS -Wl,--as-needed -Wl,--no-undefined)

add_subdirectory(pyscical)
add_subdirectory(bin)
add_subdirectory(lib)
