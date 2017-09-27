Installation
============

To install wopmars, you have to get the sources and go to source folder::

    git clone git@github.com:aitgon/wopmars.git
    cd wopmars

Then you go to the WopMars source directory and type::

    pip install . # install wopmars

Installation in a Miniconda Environment
---------------------------------------

Then we recommend to use a `Miniconda <https://conda.io/miniconda.html>`_ environment

.. code-block:: bash

    conda create --name wopmars python=3 # create environment
    conda install --yes --name wopmars --file spec-file.txt # install some packages through conda
    pip install -r requirements.txt # install other packages through pip
    pip install . # install wopmars

Installation in a Virtualenv Environment
------------------------------------------

.. code-block:: bash

    virtualenv --python=/usr/bin/python3 wopmarsenv
    source wopmarsenv/bin/activate
    pip install -r requirements.txt # install other packages through pip
    pip install . # install wopmars

Installation with MariaDB/MySQL
------------------------------------------

To use wopmars with the MariaDB/MySQL database engine, you need to install the python MySQL client::

    pip install mysqlclient

Issues with PyGraphviz
------------------------------------------

If you do not have permission for the ``sudo``, you should use the command line ::

    python3 setup.py install --no-pygraphviz

But you won't be able to run the ``--dot`` option on WopMars.

Otherwise you will need some or all these packages::

    sudo apt-get install graphviz-dev libcgraph6
    sudo apt-get install python3-tk


