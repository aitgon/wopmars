"""A setuptools based setup module of WopMars

See:
"""

from setuptools import setup, find_packages
from codecs import open
from os import path
import sys

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

with open('requirements.txt') as f:
    required = f.read().splitlines()


if '--no-pygraphviz' in sys.argv:
    for package in required:
        if 'pygraphviz' in package:
            required.remove(package)
            sys.argv.remove('--no-pygraphviz')


setup(
    name='wopmars',
    version='1.1.2',
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
    packages=find_packages(exclude=['log', 'doc', '*.test.*', 'soutenance', 'rapport']),
    install_requires=required,
    data_files=[],
    entry_points={
        'console_scripts':['wopmars=wopmars:run']
    },
    package_data={},
    include_package_data=True
)
