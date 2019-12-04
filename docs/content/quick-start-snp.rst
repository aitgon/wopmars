Quick Start 2 - SNP Example
============================

This example has been used to test the performance of WopMars in our paper with different amount of data and database engine and access method (Ref). Single nucleotide polymorphismes (SNPs) are very variable position in the genome. Many SNPs have been statistically associated to diseases or phenotypes. This workflow is used to fill in a database that relates SNPs and phenotypes (Ref).

The database access methods are: **SQLAlchemy ORM** and **core**. We have defined three different wopfiles using different wrappers for each of these methods.

To build the workflow files architecture, go to any directory and type the following command::
    
    wopmars example_snp

You'll get the following files architecture::

    $ tree wopmars_example_snp |grep -v __init__
    wopmars_example_snp
    ├── data
    │   ├── snp2phenotype.tsv
    │   ├── snp.tsv
    │   ├── WopfileCore.yml
    │   ├── WopfileOrm.yml
    ├── output
    ├── setup.py
    └── wopexamplesnp
        ├── model
        │   ├── Phenotype.py
        │   ├── SNP2Phenotype.py
        │   └── SNP.py
        └── wrapper
            ├── core
            │   ├── InsertPhenotype.py
            │   ├── InsertSNP2Phenotype.py
            │   └── InsertSnp.py
            ├── orm
            │   ├── InsertPhenotype.py
            │   ├── InsertSNP2Phenotype.py
            │   └── InsertSnp.py

Move to `wopmars_example_snp` directory and install the package *wopexample*::

    cd wopmars_example_snp
    pip install .

Go to console and select one of the wopfiles:

.. code-block:: bash

    export WOPFILE=$PWD/data/WopfileOrm.yml

.. code-block:: bash

    export WOPFILE=$PWD/data/WopfileCore.yml

With this code you can run the workflow using the **SQLite** database engine.

.. code-block:: bash

    wopmars -w $WOPFILE -D "sqlite:///output/db.sqlite" -v -p

To run the workflow with the **MariaDB/MySQL** database engine, you must first create a user and a database, eg. __wopdb__ and __wopuser__ with __mypass__ password. Then the command to run wopmars is:

.. code-block:: bash

    wopmars -w $WOPFILE -D "mysql://wopuser:mypass@localhost/wopdb" -d $PWD -v -p

To run the workflow with the **PostgreSQL** database engine, you must first create a user and database, eg. __wopdb__ and __wopuser__ with __mypass__ password. Then the command to run wopmars is:

.. code-block:: bash

    wopmars -w $WOPFILE -D "postgresql://wopuser:mypass@localhost/wopdb" -d $PWD -v -p

Now you can show the database tables using

.. code-block:: bash

    $ sqlite3 output/db.sqlite '.table'
    Phenotype               wom_file                wom_table_io_information             
    SNP                     wom_modification_table  wom_type_input_or_output              
    SNP2Phenotype           wom_option            
    wom_execution           wom_rule

And then check the content of some table with

.. code-block:: bash

    $ sqlite3 output/db.sqlite 'select * from SNP'
    1|1|209815925|642961
    2|17|56699594|227727

You can now develop your Wopmars workflow with the help of the following :doc:`Wopfile </content/wopfile>`, :doc:`Wrapper </content/wrapper>` and :doc:`Model </content/model>` sections.

