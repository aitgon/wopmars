Installation
============

To install wopmars, you have to get the sources on the git repository and then go to the source directory and type::

    pip install .

To use wopmars with the MariaDB/MySQL database engine, you need to install the python MySQL client

    pip install mysqlclient

.. warning::

    There could be some issues regarding the `pygraphviz` package. 

    - If you do not have permission for the ``sudo``, you should use the command line ::

        python3 setup.py install --no-pygraphviz

    But you won't be able to run the ``--dot`` option on WopMars.

    - Else, install `graphviz-dev` and `libcgraph6`::
    
        sudo apt-get install graphviz-dev libcgraph6

