Quick Start - Car Example
==========================

Now you should be able to run WopMars for the first time and we have prepared a simple example of workflow to introduce you to the basics of WopMars.

To build the workflow files architecture, go to any directory and type the following command::
    
    wopmars example

You'll get the following files architecture::

    $ tree wopmars_example/ |grep -v __init__
    wopmars_example/
    ├── input
    │   └── pieces.txt
    ├── output
    ├── setup.py
    ├── wopexample
    │   ├── models
    │   │   ├── DatedPiece.py
    │   │   ├── PieceCar.py
    │   │   └── Piece.py
    │   └── wrappers
    │       ├── AddDateToPiece.py
    │       ├── CarAssembler.py
    │       └── SparePartsManufacturer.py
    ├── Wopfile
    ├── Wopfile2
    └── Wopfile3

Move to `wopmars_example` directory and install the package *wopexample*::

    cd wopmars_example
    pip install .

.. note::
    You have just installed your first **WopMars Package**, congratulations! Every *Toolwrapper* for WopMars is supposed to be built in a package in order to be easily installed.


Now, let's look in the `Wopfile`

.. code-block:: yaml

    # Rule1 use SparePartsManufacturer to insert pieces informations into the table piece
    rule Rule1:
        tool: 'wopexample.wrapper.SparePartsManufacturer'
        input:
            file:
                pieces: 'input/pieces.txt'
        output:
            table:
                piece: 'wopexample.model.Piece'

    # CarAssembler make the combinations of all possible pieces to build cars and calculate the final price
    rule Rule2:
        tool: 'wopexample.wrapper.CarAssembler'
        input:
            table:
                piece: 'wopexample.model.Piece'
        output:
            table:
                piece_car: 'wopexample.model.PieceCar'
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

Now that you have run a working example you can go to the :doc:`Wopfile </content/wopfile>`, :doc:`Wrapper </content/wrapper>`, or :doc:`Model </content/model>` sections to develop your own Wopmars workflow. In the next section, you have a bioinformatics example.

