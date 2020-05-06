# -*- coding: UTF-8 -*-

__author__ = "Aitor Gonzalez, Luc Giffon, Lionel Spinelli"
__copyright__ = "Copyright: since 2017, Aitor Gonzalez, Luc Giffon, Lionel Spinelli"
__email__ = "aitor.gonzalez@univ-amu.fr"
__license__ = "MIT"

from codecs import open
from os import path
import sys
import os
from configparser import RawConfigParser


def get_version():
    """Return package version from setup.cfg."""
    config = RawConfigParser()
    config.read(os.path.join('.', 'setup.cfg'))
    return config.get('metadata', 'version')


if sys.version_info < (3, 6):
    print("Python version >= 3.6 required.")

try:
    from setuptools import setup, find_packages
except ImportError:
    print("Please install setuptools before installing wopmars.",
          file=sys.stderr)
    exit(1)

here = os.path.abspath(os.path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as fin:
    long_description = fin.read()

CLASSIFIERS = """\
Development Status :: 4 - Beta
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
Topic :: Scientific/Engineering :: Bioinformatics
Topic :: Scientific/Engineering :: Information Analysis
Topic :: Software Development
Operating System :: POSIX :: Linux
"""

setup(name='wopmars',
    version=str(get_version()),
    description='Workflow Python Manager for Reproducible Science',
    long_description=long_description,
    url='https://github.com/aitgon/wopmars',
    author=__author__,
    author_email=__email__,
    license=__license__,
    classifierss=[_f for _f in CLASSIFIERS.split('\n') if _f],
    download_url='https://github.com/aitgon/wopmars/archive/%s.tar.gz'%str(get_version()),
    keywords='workflow manager python object-oriented reproducible science database framework',
    packages=find_packages(exclude=['log', 'doc', '*.test_bak.*', 'soutenance', 'rapport']),
    install_requires = ["SQLAlchemy>=1.1.11", "docopt>=0.6.2", "schema>=0.6.2", "termcolor>=1.1.0", "PyYAML>=3.12", "networkx>=2.4"],
    extras_require={'pygraphviz': ['pygraphviz',]},
    data_files=[],
    entry_points={
        'console_scripts':['wopmars=wopmars:run']
    },
    package_data={},
    include_package_data=True
)

