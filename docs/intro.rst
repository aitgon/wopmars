
Introduction
============

The connection between the results of a tool and their insertion into the database is done thanks to Python classes called *wrappers* compatible with WoPMaRS. These wrapper classes are able to both wrap the execution command line of an analysis tool and perform *pre* or *post* data processing (like, for example, gather data from the database or insert them).

Here comes two use-cases which are:

- **develop** wrapper classes also called *ToolWrappers*
- **use** these *ToolWrappers* to perform an analysis workflow

Prerequisites
-------------

Using WoPMaRS
*************

- Basic knowledge on relational databases
- Basic knowledge on command line use

Developping *ToolWrappers*
**************************

- Basic knowledge on Python (controling structures `if/else/elif`, loops `while/for`, declaring and using variables and exception handling)
- More advanced knowledge in relational databases (data types, selecting and modificating rows, primary keys and foreign keys)
- Understanding Object Oriented Programming in Python is recommended
- Basic knowledge on the use of SQLAlchemy

Installation
------------

To install wopmars, you have to get the sources on the git repository and then go to the source directory and type::

    pip install .

.. warning::

    There could be some issues regarding the `pygraphviz` package. 

    - If you do not have permission for the `sudo`, you should use the command line ::

        python3 setup.py install --no-pygraphviz

    But you won't be able to run the `--dot` option on WoPMaRS.

    - Else, install graphviz-dev and libcgraph6::
    
        sudo apt-get install graphviz-dev libcgraph6


Basic Usage
-----------

Now you should be able to run WoPMaRS for the first time and we have prepared a simple example of workflow to introduce you to the basics of WoPMaRS.

To build the workflow files architecture, go to any directory and type the following command::
    
    wopmars example

You'll get the following files architecture::

    .
    └── wopmars_example
        ├── input
        │   └── pieces.txt
        ├── output
        ├── setup.py
        ├── wopexample
        │   ├── __init__.py
        │   ├── models
        │   │   ├── __init__.py
        │   │   ├── PieceCar.py
        │   │   └── Piece.py
        │   └── wrappers
        │       ├── CarAssembler.py
        │       ├── __init__.py
        │       └── SparePartsManufacturer.py
        └── Wopfile

Move to `wopmars_example` directory and install the package *wopexample*::

    cd wopmars_example
    pip install .

.. note::
    You have just installed your first **WoPMaRS Package**, congratulations! Every *ToolWrapper* for WoPMaRS is supposed to be built in a package in order to be easily installed.


Now, let's look in the `Wopfile`::

    rule Rule1:
        tool: 'wopexample.wrappers.SparePartsManufacturer'
        input:
            file:
                pieces: 'input/pieces.txt'
        output:
            table:
                piece: 'wopexample.models.Piece'

    rule Rule2:
        tool: 'wopexample.wrappers.CarAssembler'
        input:
            table:
                piece: 'wopexample.models.Piece'
        output:
            table:
                piece_car: 'wopexample.models.PieceCar'
        params:
            max_price: 2000


There are two rules named `Rule1` and `Rule2`. It means that the workflow is composed of two steps. For each rule, the used *ToolWrapper*, its parameters (if needed), inputs and outputs are specified. If you look closely at the values of these inputs and outputs, you can notice that the output of the `Rule1` has the exact same value than the input of the `Rule2`: `wopexample.models.Piece`. It means that the `Rule1` will write into the table associated with the Model `Piece` and the `Rule2` will read these writes. Therefore, `Rule2` won't run before `Rule1` because there is a *dependency relation* between them.

.. note::

    Have you noticed the path to the models for the `tool` and `table` parts? The path to the different modules are explicitly specified to prevent ambiguity. 

It came time to start your first workflow!

.. code-block:: python
    wopmars -w Wopfile -D output/wopmars.sqlite -vvv -p

You will see a little bit of output in the console thanks to the `-p` coupled with the `-vvv` option which describe the work processed by WoPMaRS. The `-D` option allows to specify the path to the database file and, you have probably realized, the `-w` option allows to specify the path to the **Workflow Definition File**.

























