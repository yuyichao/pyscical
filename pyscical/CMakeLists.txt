python_install_module(pyscical
  astro.py
  atomic.py
  atom_mass.py
  _cffi.py
  constants.py
  _const.py
  formatter.py
  __init__.py
  _ipython.py
  units.py
  value.py)

python_install_module(pyscical/ocl
  ocl/__init__.py
  ocl/elwise.py
  ocl/ode.py
  ocl/utils.py)

install(FILES ocl/cl/pyscical-ode.cl
  DESTINATION "${PYTHON_SITE_PACKAGES_INSTALL_DIR}/pyscical/ocl/cl")
