set(pyscical_SRCS
  atomic.c
  math.cpp)

add_library(pyscical SHARED
  ${pyscical_SRCS})

target_link_libraries(pyscical ${qtcurve_utils_LINKS})

set_target_properties(pyscical PROPERTIES
  COMPILE_FLAGS "-fvisibility=hidden"
  LINK_FLAGS "-Wl,--no-undefined"
  LIBRARY_OUTPUT_DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}"
  PREFIX ""
  OUTPUT_NAME "_pyscical")
install(TARGETS pyscical LIBRARY
  DESTINATION "${PYTHON_SITE_PACKAGES_INSTALL_DIR}/pyscical")
install(FILES api.h
  DESTINATION "${PYTHON_SITE_PACKAGES_INSTALL_DIR}/pyscical")
