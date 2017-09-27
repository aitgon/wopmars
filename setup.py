"""A setuptools based setup module of WopMars

See:
"""

from setuptools import setup, find_packages
from codecs import open
from os import path
import sys

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

with open('requirements.txt') as f:
    required = f.read().splitlines()

if '--nopygraphviz' in sys.argv:
    for package in required:
        if 'pygraphviz' in package:
            required.remove(package)
            sys.argv.remove('--nopygraphviz')

setup(
    cmdclass={
        'foo': CustomInstallClass,
    },
    name='wopmars',
    version='1.1.9',
    description='Workflow Python Manager for Reproducible Science',
    long_description=long_description,
    # todo ask aitor url home page
    url='',
    author='Luc Giffon - TAGC',
    author_email='luc.giffon@gmail.com',
    # todo ask aitor license
    license='',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Programming Language :: Python :: 3.4',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        #todo License::
        'Environment :: Console',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.4',
        'Topic :: Database :: Front-Ends',
        'Topic :: Adaptive Technologies',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Topic :: Software Development',
    ],
    keywords='workflow manager python object-oriented reproducible science database framework',
    packages=find_packages(exclude=['log', 'doc', '*.test_bak.*', 'soutenance', 'rapport']),
    install_requires=required,
    data_files=[],
    entry_points={
        'console_scripts':['wopmars=wopmars:run']
    },
    package_data={},
    include_package_data=True
)

