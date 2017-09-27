.. WopMars documentation master file, created by
   sphinx-quickstart on Wed Jul 27 13:45:18 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to WopMars's documentation!
===================================

**WopMars** is an implicity workflow manager based on a workflow definition file (wopfile) similar to `GNU Make <https://www.gnu.org/software/make/>`_ or `Snakemake <https://snakemake.readthedocs.io/en/stable/>`_ written in Python. In addition to files, WopMars takes advantages of `SQLAlchemy <https://www.sqlalchemy.org/>`_ to use database models as inputs and outputs in the workflow. It has been developed in a bioinformatics context and it is particularly useful when the analysis results must be stored in a relational database.

Pros and Cons of WopMars
---------------------------

- Pros:

   - Simplified data analysis and sharing based on relational database storage
   - Full SQL power and flexibility based on the SQL Alchemy ORM
   - Track of analysis history for more result reproducibility
   - Feed your database over time

- Cons:

   - Performance cost of database reading and writing
   - No parallel execution of rule
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

