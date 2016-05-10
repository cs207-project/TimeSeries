"""
setup.py file for SWIG example
"""

from setuptools import setup, Extension
setup(name='interface',
    version='0.1',
    ext_modules=[Extension('_interface', sources=['fft.cpp','interface.i'],
                    swig_opts=['-c++'],
                    )],
    headers=['fft.h']
)