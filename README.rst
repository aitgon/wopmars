WopMars: Workflow Python Manager for Reproducible Science
======================================================================

.. image:: https://img.shields.io/pypi/v/wopmars.svg
    :target: https://pypi.python.org/pypi/wopmars

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

You can install the latest WopMars version via "pypi":

.. code-block:: bash

    pip install wopmars

Run a quick example:

.. code-block:: bash

    wopmars example
    cd example
    pip install -e .
    wopmars -D sqlite:///db.sqlite -w Wopfile.yml -v

If there were not errors, you can look at the content of the sqlite db.

.. code-block:: bash

    $ sqlite3 db.sqlite '.tables'

    Piece                            wom_TableInputOutputInformation
    PieceCar                         wom_TableModificationTime
    wom_Execution                    wom_ToolWrapper
    wom_FileInputOutputInformation   wom_TypeInputOrOutput
    wom_Option

    $ sqlite3 db.sqlite "select * from Piece limit 5"

    1|UC8T9P7D0F|wheel|664.24
    2|2BPN653B9D|engine|550.49
    3|T808AHY3DS|engine|672.09
    4|977FPG7QJZ|bodywork|667.23
    5|KJ6WPB3N56|engine|678.83

The `WopMars documentation <http://wopmars.readthedocs.org/>`_ with user guide and
API reference is hosted at Read The Docs.

