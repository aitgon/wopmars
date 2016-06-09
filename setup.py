"""A setuptools based setup module of WopMars

See:
"""

from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='wopmars',
    version='1.1.0',
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
    package_data={},
    data_files=[],
)
