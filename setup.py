import os
import sys
import inspect
import pathlib
import setuptools
from setuptools import setup


package_dir = '.' # the directory that would get added to the path, expressed relative to the location of this setup.py file



try: __file__
except:
	try: frame = inspect.currentframe(); __file__ = inspect.getfile( frame )
	finally: del frame  # https://docs.python.org/3/library/inspect.html#the-interpreter-stack
HERE = os.path.realpath( os.path.dirname( __file__ ) )
HERE2 = pathlib.Path(__file__).parent

long_description = (HERE2 / "long_description.txt").read_text()

setup_args = dict(name='PyGrabIt',
package_dir={ '' : package_dir },
	  version='0.0.8', # @VERSION_INFO@
	  description='Python implementation of grabit toolbox.',
	  long_description=long_description,
	  url='https://github.com/ludvikalkhoury/PyGrabIt.git',
	  author='Ludvik Alkhoury',
	  author_email='Ludvik.Alkhoury@gmail.com',
	  packages=['PyGrabIt'],
	  install_requires=['Pillow>=9.4.0'])
	  
	  
if __name__ == '__main__' and getattr( sys, 'argv', [] )[ 1: ]:
	setuptools.setup( **setup_args )
else:
	sys.stderr.write( """
The `PyGrabIt` setup.py file should not be run or imported directly.
Instead, it is used as follows::

	python -m pip install -e  "%s"

""" % HERE )

