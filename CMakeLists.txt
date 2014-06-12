project(QtCurve)

## Setup
cmake_minimum_required(VERSION 2.8)
set(CMAKE_MODULE_PATH "${CMAKE_MODULE_PATH}"
  "${CMAKE_CURRENT_SOURCE_DIR}/cmake")

include(PythonMacros)

# ## Version
# set(PYSCICAL_VERSION_MAJOR "0")
# set(PYSCICAL_VERSION_MINOR "1")
# set(PYSCICAL_VERSION_PATCH "0")
# set(PYSCICAL_VERSION "${PYSCICAL_VERSION_MAJOR}.${PYSCICAL_VERSION_MINOR}")
# set(PYSCICAL_VERSION_FULL "${PYSCICAL_VERSION}.${PYSCICAL_VERSION_PATCH}")

if(NOT BIN_DIR)
  set(BIN_DIR bin)
endif()

add_subdirectory(pyscical)
add_subdirectory(bin)
