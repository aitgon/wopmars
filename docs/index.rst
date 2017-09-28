.. WopMars documentation master file, created by
   sphinx-quickstart on Wed Jul 27 13:45:18 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to WopMars's documentation!
===================================

.. image:: https://travis-ci.org/aitgon/wopmars.svg?branch=master
    :target: https://travis-ci.org/aitgon/wopmars

.. image:: https://readthedocs.org/projects/wopmars/badge/?version=latest
    :target: http://wopmars.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. image:: https://img.shields.io/pypi/v/wopmars.svg
    :target: https://pypi.python.org/pypi/wopmars

**WopMars** is an implicity workflow manager based on a workflow definition file written in Python that uses file and database input/outputs to create and follow the execution direct acyclic graph (DAG). It has been developed in a bioinformatics context and it is particularly useful when the analysis results must be stored in a relational database.

Pros and Cons of WopMars
---------------------------

- Pros:

   - Simplified data analysis and sharing based on relational database storage
   - Full SQL power and flexibility based on the SQL Alchemy ORM
   - Track of analysis history for more result reproducibility
   - Feed your database over time

- Cons:

   - No parallel execution of rules but can be integrated in a parallel workflow that access partitioned databases (Database sharding)
   - Wrapper and model class definition is required

Table of Contents
=================

.. toctree::
   :maxdepth: 2

   content/overview
   content/installation
   content/quick-start
   content/quick-start-snp
   content/wopfile
   content/wrapper
   content/model
   content/developer

.. Indices and tables
.. ==================

.. :ref:`genindex`
.. * :ref:`modindex`
.. * :ref:`search`

