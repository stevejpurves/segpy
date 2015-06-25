from distutils.core import setup
from Cython.Build import cythonize

setup(
  name = 'ibm float fn',
  ext_modules = cythonize("ibm_float.pyx"),
)