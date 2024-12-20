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



def get_version():
	version_file = os.path.join(os.path.dirname(__file__), 'PyGrabIt', 'Library.py')
	with open(version_file, 'r') as f:
		for line in f:
			if line.strip().startswith('version'):
				# Extract the version from the line, e.g., 'versions = "0.0.11"'
				version = line.split('=')[-1].strip().strip('"')
				print('Version ' + version)
				return version
				
	raise ValueError("Version not found in PyGrabIt/Library.py")



setup_args = dict(name='PyGrabIt',
package_dir={ '' : package_dir },
	  version=get_version(), # @VERSION_INFO@
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
Instead, it is used as follows:

	python -m pip install -e  "%s"

""" % HERE )

