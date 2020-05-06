.. WopMars documentation master file, created by
   sphinx-quickstart on Wed Jul 27 13:45:18 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

WopMars: Workflow Python Manager for Reproducible Science
======================================================================

.. image:: https://img.shields.io/pypi/v/wopmars.svg
    :target: https://pypi.python.org/pypi/wopmarst

.. image:: https://img.shields.io/pypi/pyversions/wopmars.svg
    :target: https://www.python.org

.. image:: https://readthedocs.org/projects/wopmars/badge/?version=latest
    :target: http://wopmars.readthedocs.io/en/latest/?badge=latest

.. image:: https://travis-ci.org/aitgon/wopmars.svg?branch=master
    :target: https://travis-ci.org/aitgon/wopmars

.. image:: https://codecov.io/gh/aitgon/wopmars/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/aitgon/wopmars

WopMars is a database-driven workflow manager written in python similar to GNU Makefile or Snakemake.
The difference is that the definition file of WopMars takes into account input/output SQLITE table defined as python
paths to SQLAlchemy models.

.. toctree::
   :maxdepth: 2

   content/overview
   content/install
   content/quick-start
   content/wopfile
   content/wrapper
   content/model
   content/cheatsheet
..   content/developer # must be updated to latest version

.. Indices and tables
.. ==================

.. :ref:`genindex`
.. * :ref:`modindex`
.. * :ref:`search`

