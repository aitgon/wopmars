
Introduction
============

The connection between the results of a tool and their insertion into the database is done thanks to Python classes called *wrappers* compatible with WoPMaRS. These wrapper classes are able to both wrap the execution command line of an analysis tool and perform *pre* or *post* data processing (like, for example, gather data from the database or insert them).

Here comes two use-cases which are:

- **use** these *ToolWrappers* to perform an analysis workflow
- **develop** wrapper classes also called *ToolWrappers*

Prerequisites
-------------

Using WoPMaRS
*************

- Basic knowledge on relational databases
- Basic knowledge on command line use

Developping *ToolWrappers*
**************************

- Basic knowledge on Python (controling structure `if/else/elif`, loops `while/for`, declaring and using variables and exception handling)
- More advanced knowledge in relational databases (data types, selecting and modificating rows, primary keys and foreign keys)
- Understanding Object Oriented Programming in Python is recommended
- Basic knowledge on the use of SQLAlchemy

Installation
------------

To install wopmars, you have to get the sources on the git repository and then go to the source directory and type:

.. code-block::
    pip install .

If you try to install WoPMaRS on a machine on which you do not have the `sudo`, there could be some issues regarding the pygraphviz package. You should use the command line :

.. code-block::
    python3 setup.py install --no-pygraphviz

But you won't be able to run the `--dot` option on WoPMaRS.


Basic Usage
-----------

Now you should be able to run WoPMaRS for the first time and we have prepared a simple example of workflow to introduce you to the basics of WoPMaRS.

To build the workflow files architecture, go to any directory and type the following command::
    
    wopmars example




.. code-block:: yaml

    rule Rule1:
        tool: 'wopmars.example.SparePartsManufacturer'
        input:
            files:
                pieces: ''















