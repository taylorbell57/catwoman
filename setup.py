from __future__ import print_function
from distutils.core import setup
from setuptools import setup
from distutils.extension import Extension
import numpy as np
from distutils.ccompiler import new_compiler
import os
import sys
import tempfile


"""
Check for OpenMP based on
https://github.com/MDAnalysis/mdanalysis/tree/develop/package/setup.py
retrieved 06/15/15
"""
def detect_openmp():
	"""Does this compiler support OpenMP parallelization?"""
	compiler = new_compiler()
	print("Checking for OpenMP support... ")
	hasopenmp = hasfunction(compiler, 'omp_get_num_threads()')
	needs_gomp = hasopenmp
	if not hasopenmp:
		compiler.add_library('gomp')
	hasopenmp = hasfunction(compiler, 'omp_get_num_threads()')
	needs_gomp = hasopenmp
	if hasopenmp: print("Compiler supports OpenMP")
	else: print( "Did not detect OpenMP support.")
	return hasopenmp, needs_gomp

def hasfunction(cc, funcname, include=None, extra_postargs=None):
	# From http://stackoverflow.com/questions/
	#            7018879/disabling-output-when-compiling-with-distutils
	tmpdir = tempfile.mkdtemp(prefix='hasfunction-')
	devnull = oldstderr = None
	try:
		try:
			fname = os.path.join(tmpdir, 'funcname.c')
			f = open(fname, 'w')
			if include is not None:
				f.write('#include %s\n' % include)
			f.write('int main(void) {\n')
			f.write('    %s;\n' % funcname)
			f.write('}\n')
			f.close()
			# Redirect stderr to /dev/null to hide any error messages
			# from the compiler.
			# This will have to be changed if we ever have to check
			# for a function on Windows.
			devnull = open('/dev/null', 'w')
			oldstderr = os.dup(sys.stderr.fileno())
			os.dup2(devnull.fileno(), sys.stderr.fileno())
			objects = cc.compile([fname], output_dir=tmpdir, extra_postargs=extra_postargs)
			cc.link_executable(objects, os.path.join(tmpdir, "a.out"))
		except Exception as e:
			return False
		return True
	finally:
		if oldstderr is not None:
			os.dup2(oldstderr, sys.stderr.fileno())
		if devnull is not None:
			devnull.close()

#checks whether OpenMP is supported
has_openmp, needs_gomp = detect_openmp()
parallel_args = ['-fopenmp', '-std=c99'] if has_openmp else ['-std=c99']
parallel_libraries = ['gomp'] if needs_gomp else []

_nonlinear_ld = Extension('catwoman._nonlinear_ld', ['c_src/_nonlinear_ld.c'], extra_compile_args = parallel_args, libraries = parallel_libraries) 
_quadratic_ld = Extension('catwoman._quadratic_ld', ['c_src/_quadratic_ld.c'], extra_compile_args = parallel_args, libraries = parallel_libraries) 
_logarithmic_ld   = Extension('catwoman._logarithmic_ld', ['c_src/_logarithmic_ld.c'], extra_compile_args = parallel_args, libraries = parallel_libraries) 
_exponential_ld   = Extension('catwoman._exponential_ld', ['c_src/_exponential_ld.c'], extra_compile_args = parallel_args, libraries = parallel_libraries) 
_custom_ld   = Extension('catwoman._custom_ld', ['c_src/_custom_ld.c'], extra_compile_args = parallel_args, libraries = parallel_libraries) 
_power2_ld   = Extension('catwoman._power2_ld', ['c_src/_power2_ld.c'], extra_compile_args = parallel_args, libraries = parallel_libraries) 
_rsky = Extension('catwoman._rsky', ['c_src/_rsky.c'], extra_compile_args = parallel_args, libraries = parallel_libraries)
_eclipse = Extension('catwoman._eclipse', ['c_src/_eclipse.c'], extra_compile_args = parallel_args, libraries = parallel_libraries)

setup(	name='catwoman', 
	version="1.0.14",
	author='Kathryn Jones',
	author_email = 'kathryndjones@hotmail.co.uk',
	url = 'https://github.com/KathrynJones1/catwoman',
	packages =['catwoman'],
	license = 'GNU GPLv3',
	description ='Transit modelling package for asymmetric light curves',
	long_description=open('README.rst').read(),
	classifiers = [
		'Development Status :: 5 - Production/Stable',
		'Intended Audience :: Science/Research',
		'Topic :: Scientific/Engineering',
		'Programming Language :: Python'
		],
	include_dirs = [np.get_include()],
	install_requires = ['numpy>=1.16.2'],
	setup_requires=['wheel','numpy>=1.16.2'],
	extras_requires= {
	    'matplotlib': ['matplotlib'],
	},
	ext_modules=[_nonlinear_ld, _quadratic_ld, _logarithmic_ld, _exponential_ld, _power2_ld, _custom_ld, _rsky, _eclipse]
)
