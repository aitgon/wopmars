WopMars: A database-driven workflow manager
------------------------------

Builds
------

+---------------------+------------------------------------------------------------------------------+
| ``master``          | .. image:: https://travis-ci.org/aitgon/wopmars.svg?branch=master             |
|                     |     :target: https://travis-ci.org/aitgon/wopmars                             |
+---------------------+------------------------------------------------------------------------------+
| ``develop`` | .. image:: https://travis-ci.org/aitgon/wopmars.svg?branch=develop    |
|                     |     :target: https://travis-ci.org/aitgon/wopmars                             |
+---------------------+------------------------------------------------------------------------------+

WopMars is a database-driven workflow manager written in python similar to GNU Makefile or Snakemake. The originality of WopMars is that it is closely connected to a relational database and can take database tables as inputs and outputs in the definition file. WopMars uses SQLAlchemy object relational mapper (ORM) and has been currently tested with SQLite, MariaDB/MySQL and PostgreSQL.



Installation
------------

To install wopmars, you have to get the sources on the git repository and then go to the source directory and type::

    pip install .

Documentation
------------

Go to the **docs** folder and type::

    make html

