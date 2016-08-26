Introduction
============

The connection between the results of a tool and their insertion into the database is done thanks to Python classes called *wrappers* compatible with WoPMaRS. These wrapper classes are able to both wrap the execution command line of an analysis tool and perform *pre* or *post* data processing (like, for example, gather data from the database or insert them).

Here comes two use-cases which are:

- **develop** wrapper classes also called *Toolwrappers*
- **use** these *Toolwrappers* to perform an analysis workflow

Table of Content
----------------

.. toctree::

   intro 

Prerequisites
-------------

Using WoPMaRS
*************

- Basic knowledge on relational databases
- Basic knowledge on command line use

Developing *ToolWrappers*
*************************

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

    - If you do not have permission for the ``sudo``, you should use the command line ::

        python3 setup.py install --no-pygraphviz

    But you won't be able to run the ``--dot`` option on WoPMaRS.

    - Else, install `graphviz-dev` and `libcgraph6`::
    
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
    You have just installed your first **WoPMaRS Package**, congratulations! Every *Toolwrapper* for WoPMaRS is supposed to be built in a package in order to be easily installed.


Now, let's look in the `Wopfile`

.. code-block:: yaml

    # Rule1 use SparePartsManufacturer to insert pieces informations into the table piece
    rule Rule1:
        tool: 'wopexample.wrappers.SparePartsManufacturer'
        input:
            file:
                pieces: 'input/pieces.txt'
        output:
            table:
                piece: 'wopexample.models.Piece'

    # CarAssembler make the combinations of all possible pieces and calculate the final price
    rule Rule2:
        tool: 'wopexample.wrappers.CarAssembler'
        input:
            table:
                piece: 'wopexample.models.Piece'
        output:
            table:
                piece_car: 'wopexample.models.PieceCar'
        params:
            # The price have to be under 2000!
            max_price: 2000


There are two rules named `Rule1` and `Rule2`. It means that the workflow is composed of two steps. For each rule, the used *Toolwrapper*, its parameters (if needed), inputs and outputs are specified. If you look closely at the values of these inputs and outputs, you can notice that the output of the `Rule1` has the exact same value than the input of the `Rule2`: ``wopexample.models.Piece``. It means that the `Rule1` will write into the table associated with the Model `Piece` and the `Rule2` will read these writes. Therefore, `Rule2` won't run before `Rule1` because there is a *dependency relation* between them.

.. note::

    Have you noticed the path to the models for the ``tool`` and ``table`` parts? The path to the different modules are explicitly specified to prevent ambiguity. 

It came time to start your first workflow!

.. code-block:: python

    wopmars -w Wopfile -D output/wopmars.sqlite -vvv -p

You will see a little bit of output in the console thanks to the ``-p`` coupled with the ``-vvv`` option which describe the work processed by WoPMaRS. The ``-D`` option allows to specify the path to the database file and, you have probably realized, the ``-w`` option allows to specify the path to the **Workflow Definition File**.

Looking at results
******************

Now, I'll show you a brief overview of what you can do with the database. First, make sure you have installed `sqlite3` on your machine::

    sudo apt-get install sqlite3

Then, open the database using sqlite::

    cd output
    sqlite3 wopmars.sqlite

.. warning::

    If you get an error `Unable to open database "wopmars.sqlite": file is encrypted or is not a database`. Make sure to use `sqlite3` instead of `sqlite`.

The preceding workflow had two steps:

1. Get pieces references in the `input/pieces.txt` file and insert them in the table `piece` of the database

.. code-block:: sql

    sqlite> SELECT * FROM piece;
    1|UC8T9P7D0F|wheel|664.24
    2|2BPN653B9D|engine|550.49
    3|T808AHY3DS|engine|672.09
    4|977FPG7QJZ|bodywork|667.23
    5|KJ6WPB3N56|engine|678.83
    6|C71CQA0OP2|wheel|643.7
    7|518SVJ81BV|bodywork|744.15
    8|PELSRMD8TZ|wheel|646.13
    9|YWL0MK7ACX|bodywork|909.75
    10|8Z59Q9AFEX|bodywork|594.44
    11|E83B8KGTVQ|wheel|978.16
    12|XQ7D1DITW4|bodywork|578.58
    13|RUN7ZM09T1|wheel|783.2
    14|DFTITSG853|wheel|776.57
    15|Y5D5BTEXIY|wheel|618.89
    16|LS8WABU4JN|engine|916.34
    17|EMYJH4TLYG|bodywork|611.92
    18|QJ20KRBC7R|bodywork|867.01
    19|9M9KLUB6MG|wheel|859.07
    20|007PPKWZ18|bodywork|603.58

2. Build all possible cars composed of those three types of pieces and store those combinations in the table `piece_car`. Here, we select only those which have a wheel of price below 650 and the total price is below 1800

.. code-block:: sql

    sqlite> SELECT DISTINCT car_serial_number, PC.price
       ...> FROM piece_car PC, piece P 
       ...> WHERE PC.wheel_serial_number=P.serial_number
       ...> AND P.price<650
       ...> AND PC.price<1800;
    BVWQEB7NY4|1772.96
    FVGAKR6W8F|1775.2
    HCN4YNU9XJ|1797.77
    JHIAGDA3GG|1791.06
    LZVCC9LW3O|1781.3
    NERS4IU9SG|1763.82
    OIQITLOFF1|1747.96
    V9968T5YOX|1788.63
    W8LPW24SXR|1772.77

Pros and Cons
-------------

- Pros:

   - Formatting your results in order to make them easy to analyze 
   - Using `SQL` to improve analysis performance
   - Keeping track of your analyzes and enrich your database over time
   - Make your results reproducible

- Cons:

   - Read and writes in the database has a cost in time. #todo benchmarking
   - Knowledge in `Python` and `SQL` is more than suitable for an optimum use of WoPMaRS


Go further
----------

Now that you should understand the basics of WoPMaRS, I recommand you learn :doc:`how to use WoPMaRS </use>` before go to the :doc:`build of ToolWrappers </dev_wrapper>`.


























