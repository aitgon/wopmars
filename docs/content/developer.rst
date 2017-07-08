Contributing to WoPMaRs
======================

This manual is dedicated to the developers who want to improve **WopMars** by adding new features or correcting bugs.

Setting up WopMars development environment
------------------------------------------

Once you have downloaded **WopMars** from git, you should want to process the `unittests` in order to make sure that everything is ok. It is best to create a conda environment to isolate your development.

.. code-block:: bash

    conda create --name wopmars python=3

Then, install the dependencies from the ``spec-file`` and ``requirements.txt`` file in your virtual environment.

.. code-block:: bash

    conda install --yes --name wopmars --file spec-files.txt
    pip install -r requirements.txt

    
The database engine for the test is passed using an environment variable. For instance, **SQLite**:

.. code-block:: bash

    mkdir -p out && export DB_URL="sqlite:///out/db.sqlite"

**MariaDB/MySQL**:

.. code-block:: bash

    export DB_URL="mysql://wopuser:mypass@localhost/wopdb"

or **PostgreSQL**:

.. code-block:: bash

    export DB_URL="postgresql://wopuser:mypass@localhost/wopdb"

You are now ready to perform unittests then stay in the source folder and run:

.. code-block:: bash

    python3 -m unittest discover

And the tests should start and be ok. You are now ready to start improving **WopMars**

Contributing to WopMars documentation
-------------------------------------

The WopMars documentation has been done thanks to `Sphinx <http://www.sphinx-doc.org/en/stable/>`_. The documentation has been written according to the `rST format <http://docutils.sourceforge.net/rst.html>`_. There is two type of documentation in **WopMars**:

- ``docstring`` in the source code
- rST files in the ``docs`` folder. Images are stored under the ``docs/images`` folder.

To build the ``html`` documentation, go in the ``docs`` folder and type the following command:

.. code-block:: bash
    
    make html

The result will be stored in the ``docs/_build/html``.

.. note::

    If you want to see what other format are available with Sphinx, you can look at the ``Makefile``. There is an help section but only html has been tested.
    

Sub-packages descriptions
-------------------------

In this section, we will see what are the main sub-packages / folders of **WopMars** and what is inside.

bin
~~~

Basically, the executable of **WopMars** if you want to run ``wopmars``, ``bin/wopmars`` is the file you should execute.

docs
~~~~

This is the folder containing the **WopMars** documentation, written in rst. This folder contains an ``images`` folder which contains graphs and images used for the documentation.

wopmars
~~~~~~~

The sources of the project are stored here. There is three sub-directories which have self-explaining names. The ``main`` sub-package contains the actual sources of **WopMars** whereas the ``test`` one contains functional and unit tests. Both hierarchies of files follow the same pattern.

wopmars.example
++++++++++++++++++++

This package contains the examples for **WopMars**. They are ready to use examples necessary for the tutorial.

wopmars.framework
++++++++++++++++++++++

The main classes involved in **WopMars** are stored here. They are splited into three categories.

wopmars.framework.database
..........................

All the processing related to the database is done here. Every objects that should exist in order to work with the database is stored here:
the :class:`~.wopmars.framework.database.SQLManager.SQLManager` which is used to perform synchronized operations against the database, the :class:`~.wopmars.framework.database.WopMarsSession.WopMarsSession` which is used to bind the Toolwrappers to the database,  the :class:`~.wopmars.framework.database.WopMarsQuery.WopMarsQuery` which is used to create queries that use the WopMaRS machinery There is a package ``tables`` which contains the models related to the history_ of **WopMars**. Among them, the :class:`~.wopmars.framework.database.tables.ToolWrapper.ToolWrapper` class.

wopmars.framework.management
.................................

Here are the classes involved in the actual management of the workflow. Which means the building of the :class:`~.wopmars.framework.management.DAG.DAG` and the walk through it thanks to the :class:`~.wopmars.framework.management.WorkflowManager.WorkflowManager`. Also, the class responsible of the actual execution of the ToolWrappers, :class:`~.wopmars.framework.management.ToolThread.ToolThread` is stored here.

wopmars.framework.parsing
..............................

Here are the classes involved in the parsing of the workflow definition file. Among them, the :class:`~.wopmars.framework.parsing.Parser.Parser` is a pivot between the :class:`~.wopmars.framework.parsing.Reader.Reader` and the core functioning of **WopMars**.


.. _history:

The history of WopMars executions
---------------------------------

**WopMars** keeps track of what has been done thanks to an history stored in database with the prefix ``wom`` in table names.

Numerous calls to those tables are done during all the process of the parsing of the definition file and the building of the execution DAG.

.. note::

	The execution DAG is the directed acyclic graph representing the workflow about to be executed

Here is a list of the tables used for history. All of the associated models are stored under ``wopmars.framework.database.tables``. If you want more informations about the models themselves, you should follow the links to get the code documentation:

- ``wom_execution`` represented by the model :class:`~.wopmars.framework.database.tables.Execution.Execution`
- ``wom_rule`` represented by the model :class:`~.wopmars.framework.database.tables.ToolWrapper.ToolWrapper`
- ``wom_type`` represented by the model :class:`~.wopmars.framework.database.tables.Type.Type`
- ``wom_file`` represented by the model :class:`~.wopmars.framework.database.tables.IOFilePut.IOFilePut`
- ``wom_table`` represented by the model :class:`~.wopmars.framework.database.tables.IODbPut.IODbPut`
- ``wom_modification_table`` represented by the model :class:`~.wopmars.framework.database.tables.ModificationTable.ModificationTable`
- ``wom_option`` represented by the model :class:`~.wopmars.framework.database.tables.Option.Option`

.. figure:: ../images/mcd.png
   :align: center

   *Here is a detailed entity-relationship model of the history in the database*

Building the execution DAG
--------------------------

The workflow DAG is built from the workflow definition file. However, there is a post treatment of the workflow DAG to get only the rules that the user wants to execute. 

The class responsible of the parsing of the workflow definition file (and the ``tool`` command) is :class:`wopmars.framework.parsing.Reader.Reader`. The class :class:`~.wopmars.framework.parsing.Reader.Reader` aims to fill the database with the informations relatives to the workflow.

Once all informations regarding the workflow definition file have been stored in the database, the options ``--targetrule`` and ``--sourcerule`` are parsed in order to get only the rules that are intended to be executed by the user (see `Options and Arguments <use.html#options-and-arguments>`__ of WopMars).

To build the DAG itself, a class :class:`~.wopmars.framework.management.DAG.DAG` which inherit from ``networkx.DiGraph`` has been written. This class takes a set of nodes as argument and build itself by determining which nodes are following which others. Since the nodes are actually :class:`~.wopmars.framework.database.tables.ToolWrapper.ToolWrapper`, a node follows an other node if one output of the former is in the list of inputs of the last. This information is given by the method :meth:`~.wopmars.framework.database.tables.ToolWrapper.ToolWrapper.follows` of :class:`~.wopmars.framework.database.tables.ToolWrapper.ToolWrapper`.


Executing the DAG
-----------------

It is the :class:`~.wopmars.framework.management.WorkflowManager.WorkflowManager` which is responsible of executing the DAG. The main methods of this class are :meth:`~.wopmars.framework.management.WorkflowManager.WorkflowManager.run_queue` and :meth:`~.wopmars.framework.management.WorkflowManager.WorkflowManager.execute_from`. Basically, ``execute_from`` fill the queue with the `Toolwrappers` that should be executed soon and ``run_queue`` actually execute the queue after performing some tests on the inputs of the `Toolwrappers`.

Managing the DataBase
---------------------

The main class responsible of managing the database is the :class:`~.wopmars.framework.database.SQLManager.SQLManager`. This class is represented in **WopMars** as a synchronized :class:`~.wopmars.utils.Singleton.SingletonMixin`. To access the Singleton instance, all you need to to is ``SQLManager.instance()``

.. note::

    A singleton, as described in the `Wikipedia article <https://en.wikipedia.org/wiki/Singleton_pattern>_` is a design pattern which allows to access anywhere and at anytime to the same instance of a given class. In our case, this is important because the SQLManager is the object which actually access the database and this needs to be synchronized. 

The constructor of the ``SQLManager`` create the actual database and enable the foreign key support (https://www.sqlite.org/foreignkeys.html#fk_enable) in order to let the user benefit from this constraint.

To get a :class:`~.wopmars.database.WopMarsSession.WopMarsSession` associated with this SQLManager, you just need to call :meth:`~wopmars.framework.database.SQLManager.SQLManager.get_session()`` and you can use the session anywhere, in any thread and at any time. Everything is already synchronized.


----

.. autoclass:: wopmars.utils.exceptions.WopMarsException.WopMarsException
   :members:

----

.. autoclass:: wopmars.framework.database.tables.Execution.Execution
   :members:    

----

.. autoclass:: wopmars.framework.database.tables.ToolWrapper.ToolWrapper
   :members:

----

.. autoclass:: wopmars.framework.database.tables.IOFilePut.IOFilePut
   :members:

----

.. autoclass:: wopmars.framework.database.tables.IODbPut.IODbPut
   :members:

----

.. autoclass:: wopmars.framework.database.tables.Type.Type
   :members:

----

.. autoclass:: wopmars.framework.database.SQLManager.SQLManager
   :members:
      
----

.. autoclass:: wopmars.framework.database.WopMarsSession.WopMarsSession
   :members:
      
----

.. autoclass:: wopmars.framework.database.WopMarsQuery.WopMarsQuery
   :members:

----

.. autoclass:: wopmars.framework.database.tables.Option.Option
   :members:

----

.. autoclass:: wopmars.framework.management.DAG.DAG
   :members:
   
----

.. autoclass:: wopmars.framework.management.WorkflowManager.WorkflowManager
   :members:
   
----

.. autoclass:: wopmars.framework.management.ToolThread.ToolThread
   :members:
   
   
----

.. autoclass:: wopmars.framework.parsing.Parser.Parser
   :members:

----

.. autoclass:: wopmars.framework.parsing.Reader.Reader
   :members:
   :exclude-members: no_duplicates_constructor
   :member-order: bysource

   
----

.. autoclass:: wopmars.utils.Singleton.SingletonMixin
   :members:
