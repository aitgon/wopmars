Quick Start - Car Example
==========================

Now you should be able to run WopMars for the first time and we have prepared a simple example of workflow to introduce you to the basics of WopMars.

To build the workflow files architecture, go to any directory and type the following command::
    
    wopmars example

You'll get the following files architecture::

    wopexample
    |-- Wopfile.yml
    |-- Wopfile2
    |-- Wopfile3
    |-- __init__.py
    |-- bats.sh
    |-- input
    |   `-- pieces.txt
    |-- model
    |   |-- DatedPiece.py
    |   |-- Piece.py
    |   |-- PieceCar.py
    |   |-- __init__.py
    |-- output
    |-- setup.py
    `-- wrapper
        |-- AddDateToPiece.py
        |-- CarAssembler.py
        |-- SparePartsManufacturer.py
        |-- __init__.py

Move to `wopmars_example` directory and install the package *wopexample*::

    cd wopmarsexample
    pip install .

.. note::
    You have just installed your first **WopMars Package**, congratulations! Every *Toolwrapper* for WopMars is supposed to be built in a package in order to be easily installed.

Now, let's look at the `Wopfile`

.. code-block:: yaml

    # Rule1 use SparePartsManufacturer to insert pieces informations into the table piece
    rule Rule1:
        tool: 'wrapper.SparePartsManufacturer'
        input:
            file:
                pieces: 'input/pieces.txt'
        output:
            table:
                piece: 'model.Piece'

    # CarAssembler make the combinations of all possible pieces to build cars and calculate the final price
    rule Rule2:
        tool: 'wrapper.CarAssembler'
        input:
            table:
                piece: 'model.Piece'
        output:
            table:
                piece_car: 'model.PieceCar'
        params:
            # The price have to be under 2000!
            max_price: 2000

There are two rules named `Rule1` and `Rule2`. It means that the workflow is composed of two steps. For each rule, the used *Toolwrapper*, its parameters (if needed), inputs and outputs are specified. If you look closely at the values of these inputs and outputs, you can notice that the output of the `Rule1` has the exact same value than the input of the `Rule2`: ``wopexamplesnp.model..Piece``. It means that the `Rule1` will write into the table associated with the Model `Piece` and the `Rule2` will iterate_wopfile_yml_dic_and_insert_rules_in_db these writes. Therefore, `Rule2` won't run before `Rule1` because there is a *dependency relation* between them.

.. note::

    Have you noticed the path to the models for the ``tool`` and ``table`` parts? The path to the different modules are explicitly specified to prevent ambiguity. 

It came time to start your first workflow!

.. code-block:: python

    wopmars -w Wopfile -D "sqlite:///db.sqlite" -v -p

You will see a little bit of output in the console thanks to the ``-p`` coupled with the ``-v`` option which describes the work processed by WopMars. The ``-D`` option allows to specify the path to the database file and, you have probably realized, the ``-w`` option allows to specify the path to the **Workflow Definition File**.

Looking at the Results
*************************

Now, I'll show you a brief overview of what you can do with the database. First, make sure you have installed `sqlite3` on your machine::

    sudo apt-get install sqlite3

Then, open the database using sqlite::

    sqlite3 db.sqlite

.. warning::

    If you get an error `Unable to open database "db.sqlite": file is encrypted or is not a database`. Make sure to use `sqlite3` instead of `sqlite`.

The preceding workflow had two steps:

1. Get pieces references in the `input/pieces.txt` file and insert them in the table `piece` of the database

.. code-block:: bash

    $ sqlite3 -header db.sqlite "select * from piece limit 5;"
    id|serial_number|type|price
    1|UC8T9P7D0F|wheel|664.24
    2|2BPN653B9D|engine|550.49
    3|T808AHY3DS|engine|672.09
    4|977FPG7QJZ|bodywork|667.23
    5|KJ6WPB3N56|engine|678.83

2. Build all possible cars composed of those three types of pieces and store those combinations in the table `piece_car`. Here, we select only those which have a wheel of price below 650 and the total price is below 1800

.. code-block:: sql

    $ sqlite3 -header db.sqlite "SELECT DISTINCT car_serial_number, PC.price FROM piece_car PC, piece P WHERE PC.wheel_serial_number=P.serial_number AND P.price<650 AND PC.price<1800 limit 5;"
    car_serial_number|price
    2OIZ5VMM29|1781.3
    77VH8BKHTQ|1788.63
    7NT5KU38K4|1772.77
    C5ML0M7GI4|1763.82
    FHPL76QFZH|1772.96

Now that you have run a working example you can go to the :doc:`Wopfile </content/wopfile>`, :doc:`Wrapper </content/wrapper>`, or :doc:`Model </content/model>` sections to develop your own Wopmars workflow.

