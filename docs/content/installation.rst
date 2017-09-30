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

Issues with PyGraphviz
------------------------------------------

If you do not have permission for the ``sudo``, you can clone WopMars from the repository and install it with this command line ::

    git clone git@github.com:aitgon/wopmars.git
    python3 setup.py install --nopygraphviz

But you won't be able to run the ``--dot`` option on WopMars.

Otherwise you will need some or all these packages::

    sudo apt-get install graphviz-dev libcgraph6
    sudo apt-get install python3-tk


