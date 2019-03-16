#! /usr/bin/env python

# System imports
from distutils.core import *
from distutils import sysconfig

# Third-party modules - we depend on numpy for everything
import numpy

# Obtain the numpy include directory.  This logic works across numpy versions.
try:
    numpy_include = numpy.get_include()
except AttributeError:
    numpy_include = numpy.get_numpy_include()

# xcmp extension module
_xcmp = Extension("_xcmp_cpp",
                   ["xcmp.i", "xcmp_imp.cpp", "ErlThread.cpp", "countdownlatch.cpp"],
                  language = 'c++',
                  extra_compile_args=['-std=c++11', '-Wall'],
                   include_dirs = [numpy_include],
                   )

# NumyTypemapTests setup
setup(  name        = "xcmp function",
        description = "xcmp .",

        author      = "Wang Chunye",
        version     = "1.0",
        ext_modules = [_xcmp]
        )
