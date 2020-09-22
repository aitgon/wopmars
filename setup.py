# -*- coding: UTF-8 -*-

# __author__ = "Aitor Gonzalez, Luc Giffon, Lionel Spinelli"
# __copyright__ = "Copyright: since 2017, Aitor Gonzalez, Luc Giffon, Lionel Spinelli"
# __email__ = "aitor.gonzalez@univ-amu.fr"
# __license__ = "MIT"

from codecs import open
from os import path
import sys
import os
from configparser import RawConfigParser
from setuptools import setup, find_packages

try:
    import wopmars
except ImportError:
    import pip
    pip.main(['install', '-r', 'requirements.txt'])
    import wopmars

def read_setup_cfg_metadata(field):
    """Return package version from setup.cfg."""
    config = RawConfigParser()
    config.read(os.path.join('.', 'setup.cfg'))
    return str(config.get('metadata', field))


if sys.version_info < (3, 6):
    print("Python version >= 3.6 required.")

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
Topic :: Scientific/Engineering :: Bio-Informatics
Topic :: Scientific/Engineering :: Information Analysis
Topic :: Software Development
Operating System :: POSIX :: Linux
Operating System :: Microsoft :: Windows :: Windows 10
"""

# Create list of package data files
def data_files_to_list(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join('..', path, filename))
    return paths

data_file_list = data_files_to_list('wopmars/data')

setup(name='wopmars',
      version=wopmars.__version__,
      description='Workflow Python Manager for Reproducible Science',
      long_description=long_description,
      url='https://github.com/aitgon/wopmars',
      author=read_setup_cfg_metadata(field='author'),
      author_email=read_setup_cfg_metadata(field='email'),
      license=read_setup_cfg_metadata(field='license'),
      classifiers=[_f for _f in CLASSIFIERS.split('\n') if _f],
      download_url='https://github.com/aitgon/wopmars/archive/%s.tar.gz'%(wopmars.__version__),
      keywords='workflow manager python object-oriented reproducible science database framework',
      extras_require={'pygraphviz': ['pygraphviz',]},
      data_files=[],
      packages=find_packages(exclude=['log', 'doc', '*.test_bak.*', 'soutenance', 'rapport']),
      package_dir={'wopmars': 'wopmars'},
      package_data={'wopmars': data_file_list},
      include_package_data=True,
      install_requires=["PyYAML>=5.3.1", "SQLAlchemy>=1.3.16", "docopt>=0.6.2", "networkx>=2.4", "schema>=0.7.2", "termcolor>=1.1.0"],
      entry_points={'console_scripts': ['wopmars=wopmars:run']},
      )

