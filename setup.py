'''
Setup.py script.
'''

__author__ = 'riko'


from Cython.Build import cythonize
import numpy
from setuptools import setup, Extension, find_packages


try:
    use_cython = True
    from Cython.Distutils import build_ext
except ImportError:
    use_cython = False

ext = '.pyx' if use_cython else '.c'

ext_modules = [Extension("calculations", ["models/calculations/calculations"+ext])]
include_dirs = []
cmdclass = {}
if use_cython:
      print "Doing extensions: ", ext_modules
      ext_modules = cythonize(ext_modules, include_dirs=[numpy.get_include()])
      include_dirs=[numpy.get_include()]
      cmdclass.update({ 'build_ext': build_ext })

print ext_modules

setup(name='TennisModelling',
      version='1.0',
      description='Tennis modelling tool.',
      author='Erik Grabljevec',
      author_email='erikgrabljevec5@gmail.com',
      url='https://github.com/erix5son/TennisModelling',
      packages=['data_tools', 'models', 'ranking_systems'],
      py_modules = ['settings'],
      cmdclass=cmdclass,
      ext_modules=ext_modules,
      include_dirs=[include_dirs, numpy.get_include()]
)