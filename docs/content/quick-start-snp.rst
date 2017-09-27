Quick start 2 - SNP example
============================

This example has been used to test the performance of WopMars in our paper with different amount of data and database engine and access method (Ref). Single nucleotide polymorphismes (SNPs) are very variable position in the genome. Many SNPs have been statistically associated to diseases or phenotypes. This workflow is used to fill in a database that relates SNPs and phenotypes (Ref).

The database access methods are: **SQLAlchemy ORM**, **core** and **pandas read_sql** and **to_sql**. We have defined three different wopfiles using different wrappers for each of these methods.

To build the workflow files architecture, go to any directory and type the following command::
    
    wopmars example_snp

You'll get the following files architecture::

    .
    ├── data
    │   ├── snp2phenotype.tsv
    │   ├── snp.tsv
    │   ├── WopfileCore.yml
    │   ├── WopfileOrm.yml
    │   └── WopfilePandas.yml
    ├── output
    │   └── db.sqlite
    ├── setup.py
    └── wopexamplesnp
        ├── __init__.py
        ├── model
        │   ├── __init__.py
        │   ├── Phenotype.py
        │   ├── SNP2Phenotype.py
        │   └── SNP.py
        └── wrapper
            ├── core
            │   ├── __init__.py
            │   ├── InsertPhenotype.py
            │   ├── InsertSNP2Phenotype.py
            │   └── InsertSnp.py
            ├── __init__.py
            ├── orm
            │   ├── __init__.py
            │   ├── InsertPhenotype.py
            │   ├── InsertSNP2Phenotype.py
            │   └── InsertSnp.py
            └── pandas
                ├── __init__.py
                ├── InsertPhenotype.py
                ├── InsertSNP2Phenotype.py
                └── InsertSnp.py

Move to `wopmars_example_snp` directory and install the package *wopexample*::

    cd wopmars_example_snp
    pip install .

Go to console and select one of the wopfiles:

.. code-block:: bash

    export WOPFILE=$PWD/data/WopfileOrm.yml

.. code-block:: bash

    export WOPFILE=$PWD/data/WopfileCore.yml

.. code-block:: bash

    export WOPFILE=$PWD/data/WopfilePandas.yml

With this code you can run the workflow using the **SQLite** database engine.

.. code-block:: bash

    wopmars -w $WOPFILE -D "sqlite:///output/db.sqlite" -v -p

To run the workflow with the **MariaDB/MySQL** database engine, you must first create a user and a database, eg. __wopdb__ and __wopuser__ with __mypass__ password. Then the command to run wopmars is:

.. code-block:: bash

    wopmars -w $WOPFILE -D "mysql://wopuser:mypass@localhost/wopdb" -d $PWD -v -p

To run the workflow with the **PostgreSQL** database engine, you must first create a user and database, eg. __wopdb__ and __wopuser__ with __mypass__ password. Then the command to run wopmars is:

.. code-block:: bash

    wopmars -w $WOPFILE -D "postgresql://wopuser:mypass@localhost/wopdb" -d $PWD -v -p

