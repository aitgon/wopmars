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

Installation with PyGraphviz
------------------------------------------

If you want to install WopMars with pygraphviz to generate workflow images, then you need to install with:

    pip install wopmars[pygraphviz]

