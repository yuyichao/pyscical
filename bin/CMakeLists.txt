configure_file(pyscical.py.in pyscical.py)

install(FILES "${CMAKE_CURRENT_BINARY_DIR}/pyscical.py"
  DESTINATION "${BIN_DIR}" RENAME "${BIN_NAME}"
  PERMISSIONS OWNER_READ OWNER_WRITE OWNER_EXECUTE
  GROUP_READ GROUP_EXECUTE WORLD_READ WORLD_EXECUTE)
