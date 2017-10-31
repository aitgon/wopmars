# -*- coding: UTF-8 -*-

__author__ = "Luc Giffon"
__copyright__ = "Copyright 2017, Luc Giffon"
__email__ = "luc.giffon@gmail.com"
__license__ = "MIT"


from codecs import open
from os import path
import sys


if sys.version_info < (3, 5):
    print("At least Python 3.5 is required.\n", file=sys.stderr)
    exit(1)

try:
    from setuptools import setup, find_packages
except ImportError:
    print("Please install setuptools before installing wopmars.",
          file=sys.stderr)
    exit(1)

from setuptools.command.install import install
class CustomInstallClass(install):
    user_options = install.user_options + [
        ('nopygraphviz', None, 'Local installation')
        ]
    def initialize_options(self):
        self.nopygraphviz = False
        install.initialize_options(self)
    def finalize_options(self):
        self.nopygraphviz = True
        install.finalize_options(self)
    def run(self):
        pass

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()


required = [
        'cycler==0.10.0',
        'decorator==4.0.10',
        'docopt==0.6.2',
        'Jinja2==2.8',
        'MarkupSafe==1.0',
        'matplotlib==1.5.3',
        'networkx==1.11',
        'numpy==1.13.1',
        'pandas==0.20.2',
        'psycopg2==2.7.1',
        'pydotplus==2.0.2',
        'pygraphviz==1.3.1',
        'pyparsing==2.1.4',
        'python-dateutil==2.5.3',
        'pytz==2016.7',
        'PyYAML==3.12',
        'schema==0.6.5',
        'six==1.10.0',
        'SQLAlchemy==1.1.11',
        'termcolor==1.1.0'
    ]

if '--nopygraphviz' in sys.argv:
    for package in required:
        if 'pygraphviz==1.3.1' in package:
            required.remove(package)
            sys.argv.remove('--nopygraphviz')

__version__='1.1.24'

setup(
    cmdclass={
        'foo': CustomInstallClass,
    },
    name='wopmars',
    version=__version__,
    description='Workflow Python Manager for Reproducible Science',
    long_description=long_description,
    url='https://github.com/aitgon/wopmars',
    author='Luc Giffon',
    author_email='luc.giffon@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Database :: Front-Ends',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Software Development',
    ],
    download_url='https://github.com/aitgon/wopmars/archive/%s.tar.gz'%__version__,
    keywords='workflow manager python object-oriented reproducible science database framework',
    packages=find_packages(exclude=['log', 'doc', '*.test_bak.*', 'soutenance', 'rapport']),
    install_requires = required,
    data_files=[],
    entry_points={
        'console_scripts':['wopmars=wopmars:run']
    },
    package_data={},
    include_package_data=True
)

