TAGOOS : associated tag SNP boosting 
---------------------------------------------

.. image:: https://readthedocs.org/projects/wopmars/badge/?version=latest
    :target: http://tagoos.readthedocs.io/en/latest/?badge=latest

WopMars is a database-driven workflow manager written in python similar to GNU Makefile or Snakemake. The originality of WopMars is that it is closely connected to a relational database and can take database tables as inputs and outputs in the definition file. WopMars uses SQLAlchemy object relational mapper (ORM) and has been currently tested with SQLite, MariaDB/MySQL and PostgreSQL.


Installation
--------------

To install wopmars, you have to get the sources on the git repository and then go to the source directory and type::

    pip install .

To install wopmars with the --dot option to generate workflow schemes::

    pip install .[pygraphviz]

Documentation
-------------

The `WopMars documentation <http://wopmars.readthedocs.org/>`_ with user guide and
API reference is hosted at Read The Docs.

