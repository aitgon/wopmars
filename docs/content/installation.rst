Installation
============

We recomend to use a `Miniconda <https://conda.io/miniconda.html>`_ environment

.. code-block:: bash

    conda create --name wopmarsenv python=3.5 # create environment
    source activate wopmarsenv

Or a `Virtualenv <https://virtualenv.pypa.io>`_ environment

.. code-block:: bash

    virtualenv --python=/usr/bin/python3.5 wopmarsenv
    source wopmarsenv/bin/activate

Then you can install WopMars with pip

.. code-block:: bash

    pip install wopmars

Installation with MariaDB/MySQL
------------------------------------------

To use wopmars with the MariaDB/MySQL database engine, you need to install the python MySQL client::

    pip install mysqlclient

Ubuntu users also need the following package, which is not installed by default::

    sudo apt-get install libmysqlclient-dev

Installation with PostgreSQL
------------------------------------------

To use wopmars with the PostgreSQL database engine, you need to install the python PostgreSQL client::

    pip install psycopg2==2.7.4

Installation with PyGraphviz
------------------------------------------

If you want to use the "--dot" argument to generate workflow images with pygraphviz, then you need either to add pygraphviz to the WopMars base installation::

    pip install pygraphviz==1.3.1

or install WopMars with the pygraphviz package::

    pip install wopmars[pygraphviz]

