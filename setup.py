# -*- coding: UTF-8 -*-

# __author__ = "Aitor Gonzalez, Luc Giffon, Lionel Spinelli"
# __copyright__ = "Copyright: since 2017, Aitor Gonzalez, Luc Giffon, Lionel Spinelli"
# __email__ = "aitor.gonzalez@univ-amu.fr"
# __license__ = "MIT"
import codecs
from codecs import open
from os import path
import sys
import os
import configparser

try:
    from setuptools import setup, find_packages
except ImportError:
    print("Please install setuptools before installing snakemake.", file=sys.stderr)
    exit(1)

if sys.version_info < (3, 6):
    print("Python version >= 3.6 required.")

here = os.path.abspath(os.path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as fin:
    long_description = fin.read()

CLASSIFIERS = """\
Development Status :: 4 - Beta
Environment :: Console
Intended Audience :: Developers
Intended Audience :: Science/Research
License :: OSI Approved :: MIT License
Programming Language :: Python
Programming Language :: Python :: 3
Programming Language :: Python :: 3.6
Programming Language :: Python :: 3.7
Programming Language :: Python :: 3.8
Programming Language :: Python :: 3 :: Only
Topic :: Database :: Front-Ends
Topic :: Scientific/Engineering :: Bio-Informatics
Topic :: Scientific/Engineering :: Information Analysis
Topic :: Software Development
Operating System :: POSIX :: Linux
Operating System :: Microsoft :: Windows :: Windows 10
"""

def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), 'r') as fp:
        return fp.read()

def get_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith('__version__'):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")

# Create list of package data files
def data_files_to_list(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join('..', path, filename))
    return paths

data_file_list = data_files_to_list('wopmars/data')

config = configparser.RawConfigParser()
config.read(os.path.join('.', 'setup.cfg'))
author = config['metadata']['author']
email = config['metadata']['email']
license = config['metadata']['license']

setup(name='wopmars',
      version=get_version("wopmars/__init__.py"),
      description='Workflow Python Manager for Reproducible Science',
      long_description=long_description,
      url='https://github.com/aitgon/wopmars',
      author=author,
      author_email=email,
      license=license,
      classifiers=[_f for _f in CLASSIFIERS.split('\n') if _f],
      download_url='https://github.com/aitgon/wopmars/archive/%s.tar.gz'%(get_version("wopmars/__init__.py")),
      keywords='workflow manager python object-oriented reproducible science database framework',
      extras_require={'pygraphviz': ['pygraphviz',]},
      data_files=[],
      packages=find_packages(exclude=['log', 'doc', '*.test_bak.*', 'soutenance', 'rapport']),
      package_dir={'wopmars': 'wopmars'},
      package_data={'wopmars': data_file_list},
      include_package_data=True,
      install_requires=["pyyaml", "sqlalchemy", "docopt", "networkx", "schema", "termcolor"],
      entry_points={'console_scripts': ['wopmars=wopmars:run']},
      )

