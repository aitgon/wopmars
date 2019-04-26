# -*- coding: UTF-8 -*-

__author__ = "Luc Giffon"
__copyright__ = "Copyright 2017, Luc Giffon"
__email__ = "luc.giffon@gmail.com"
__license__ = "MIT"

import wopmars
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

if sys.version_info < (3, 3):
    print("At least Python 3.3 is required.\n", file=sys.stderr)
    exit(1)

try:
    from setuptools import setup, find_packages
except ImportError:
    print("Please install setuptools before installing wopmars.",
          file=sys.stderr)
    exit(1)

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(name='wopmars',
    version=str(get_version()),
    description='Workflow Python Manager for Reproducible Science',
    long_description=long_description,
    url='https://github.com/aitgon/wopmars',
    author=__author__,
    author_email=__email__,
    license=__license__,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Database :: Front-Ends',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Software Development',
    ],
    download_url='https://github.com/aitgon/wopmars/archive/%s.tar.gz'%str(get_version()),
    keywords='workflow manager python object-oriented reproducible science database framework',
    packages=find_packages(exclude=['log', 'doc', '*.test_bak.*', 'soutenance', 'rapport']),
    install_requires = ["SQLAlchemy>=1.1.11", "docopt>=0.6.2", "schema>=0.6.5", "termcolor>=1.1.0", "PyYAML>=3.12", "networkx>=2.1"],
    extras_require={'pygraphviz': ['pygraphviz',]},
    data_files=[],
    entry_points={
        'console_scripts':['wopmars=wopmars:run']
    },
    package_data={},
    include_package_data=True
)

