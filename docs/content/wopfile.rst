The Workflow definition file or wopfile
=======================================

The workflow definition file, called `Wopfile`, is the entry point for WopMars. It is very similar to `snakemake <https://bitbucket.org/snakemake/snakemake/wiki/Home>`_ or `GNU make <https://www.gnu.org/software/make/>`_ since the aim of those tools are very similar. 

A formal view of the grammar is the following::

    WopMars       = rule
    ni            = NEWLINE INDENT
    rule          = "rule" (unique)identifier ":" ruleparams
    ruleparams    = [ni tool] [ni input] [ni output] [ni params]
    filesortables = (files?|tables?)
    files         = "file"   ":" (ni identifier ”:” stringliteral)+
    tables        = "table"  ":" (ni identifier ”:” stringliteral)+
    tool          = "tool"   ":" stringliteral
    input         = "input"  ":" ni filesortables
    output        = "output" ":" ni filesortables
    params        = "params" ":" (ni identifier ”:” stringliteral)+
    (NEWLINE WopMars)+
    
Since this kind of notation is not familiar to everyone, we'll describe it in clear word. 

.. note::

    Some of you may have recognized the `yaml` syntax and you are right! The `yaml specifications <http://yaml.org/spec/>`_ must be respected in order to make WoPMars work properly. This means that you have to indent your new lines and make your file easily readable. Also, you can write comments in your workflow with the ``#`` character. Moreover, you can use double `"`, simple `'` or no quotes when assigning value to an identifier but if you choose one way, I recommand you to stick with it!
    
Wopfile example
+++++++++++++++

Since one picture says more than one thousand words, here is a self-explaining example of what a `Wopfile` should look like:

.. code-block:: yaml

    # Rule1 use SparePartsManufacturer to insert pieces informations into the table piece
    rule Rule1:
        tool: 'wopexamplesnp.wrapper..SparePartsManufacturer'
        input:
            file:
                pieces: 'input/pieces.txt'
        output:
            table:
                piece: 'wopexamplesnp.model..Piece'

    # CarAssembler make the combinations of all possible pieces and calculate the final price
    rule Rule2:
        tool: 'wopexamplesnp.wrapper..CarAssembler'
        input:
            table:
                piece: 'wopexamplesnp.model..Piece'
        output:
            table:
                piece_car: 'wopexamplesnp.model..PieceCar'
        params:
            # The price have to be under 2000!
            max_price: 2000

rule
++++

In **WoPMars**, like in other workflow managers, each ``rule`` is associated with a step of the workflow. Its name has to be unique in the whole workflow but it has no specific role for WoPMars except help you understand which step is currently running, during the execution.

A rule is composed of:

- a ``tool`` which is the full name of a `Toolwrapper`
- some ``input`` and `output` which are the file paths or the full names of the models (e.g. tables) associated with the correct name (specified by the `Toolwrapper` developper)
- some ``params``, also given in the `Toolwrapper` documentation


tool
++++

Like it has been said previously, the ``tool`` must be specified with its "full name". It means that you have to write the full path to the python module containing the `ToolWrapper`. This path is written following the Python syntax (e.g. ``.`` instead of ``/``) and must be known.

   *Example*::

       wopexamplesnp.wrapper..SparePartsManufacturer

   It is used for a package named 'wopexample' which itself contains an other package named 'wrappers' which itself contains the module of interest 'SparePartsManufacturer' (which contains the `Toolwrapper` `SparePartsManufacturer`).

input and output
++++++++++++++++

file
~~~~

Each `file` is **required** and specified with a value associated to a key. The keys are given by the `Toolwrapper` developer and they should be specified in the documentation of the `Toolwrapper`. The value is the path to the wanted file. This path can be absolute or relative to the current working directory (this can be set using the `-d` option, but we'll see it later).

table
~~~~~

Like files, each `table` is **required** and specified with a value associated to a key. The keys have a "double role": 

- First, they allow the `Toolwrapper` developper to access the right `model` (e.g. table) at the right time. 
- Second, they are supposed to stand for the table name of the `model` and WopMars can check that the `model` specified in the Wopfile is actually associated with the right table. As a value, the user have to specify the full name of the models. Like for `tool`, the "full name" means the full path in a Python syntax.

   *Example*::

       wopexamplesnp.model..Piece

   It is used for a package named 'wopexample' which itself contains an other package named 'models' which itself contains the module of interest 'Piece' (which contains the `model` `Piece`).


params
++++++

The `params` are actually some options designed by the `Toolwrapper` developer in order to parametrize the execution of his wrapper. They are often the options of the underlying tools. They shouldn't be required except if the developper has explicitly said in his documentation that they are.
`params` work following the usual key-value system.

The DAG
+++++++

Now that you understand how to specify the rules of your workflow, you may be able to see the different steps of the workflow as the different nodes of a **Directed Acyclic Graph**. The *dependency relation* between those nodes are given thanks to the state of `input` and `output` of the files and tables: if one input of a rule A is in the outputs of an other rule B, then rule A is a direct successor of rule B.

.. figure::  ../images/workflow.png
   :align:   center
   
   *You can easily see the graph on this representation of a workflow*

Command line usage
+++++++++++++++++++

Like almost every software nowadays, you can get an help about *how to use WopMars* using the ``-h`` option::

    WopMars: Workflow Python Manager for Reproducible Science.

    Usage:
      wopmars [-n] [-p] [-F] [-v...] [-d DIR] [-g FILE] [-L FILE] [-f RULE | -t RULE] [-D DATABASE] [-w DEFINITION_FILE]
      wopmars tool TOOLWRAPPER [-i DICT] [-o DICT] [-P DICT] [-p] [-F] [-D DATABASE] [-v...] [-d DIR] [-L FILE] [-g FILE]
      wopmars example [-d DIR]

    Arguments:
      DEFINITION_FILE  Path to the definition file of the workflow [default: wopfile.yml].
      DATABASE         Path to the sqlite database file
      FILE             Path to a file.
      RULE             Name of a rule in the workflow definition file.
      TOOLWRAPPER      Path the the toolwrapper
      DICT             String formated like a dictionnary. Ex: "{'input1': 'path/to/input1', 'input2': 'path/to/input2'}"

    Options:
      -h --help                    Show this help.
      -v                           Set verbosity level.
      -g FILE --dot=FILE           Write dot representing the workflow in the FILE file (with .dot extension).
      -L FILE --log=FILE           Write logs in FILE file [default: $HOME/.wopmars/wopmars.log].
      -p --printtools              Write logs in standard output.
      -f RULE --sourcerule=RULE    Execute the workflow from the given RULE.
      -t RULE --targetrule=RULE    Execute the workflow to the given RULE.
      -F --forceall                Force the execution of the workflow, without checking for previous executions.
      -n --dry-run                 Only display what would have been done.
      -d --directory=DIR           Set the current working directory. Usefull for working with relative poths [default: $CWD].
      -D --database=DATABASE       Set the path to the database [default: $CWD/Wopfile].
      -w --wopfile=DEFINITION_FILE Set the path to the definition file [default: $CWD/wopmars.sqlite].
      -i --input=DICT              Set the input of the toolwrapper you want to use in the dictionnary format.
      -o --output=DICT             Set the output of the toolwrapper you want to use in the dictionnary format.
      -P --params=DICT             Set the parameters of the toolwrapper you want to use in the dictionnary format.
      -c --clear-history           Clear WopMars history. Should be used in case of bug which seem to be related to the history. Be carefull, clearing history will result in a re-execution of the whole workflow.
      -u --update                  Should be used when a file supposedly generated by the workflow already exists and should be used as it. (Not implemented)
      -l --toolwrapper-log         Allow the toolwrapper to print its logs in the standard output. dictionnary format.
 
Let's see what is interesting in there.

Execution modes
+++++++++++++++

There are three mode for running WopMars:

1. The main mode is by default, you have already used it in the `Basics Tutorial </intro>`_ and it allows to execute a workflow from the `Wopfile`
2. The ``tool`` mode aims to execute only one `Toolwrapper`. It is usually used for debugging purposes while the `Toolwrapper` developer is actually developing the wrapper
3. You're supposed to have already used the ``example`` mode in the `Basics Tutorial </intro>`_ but if not, you should know that it aims to build a ready-to-run project example

Database engines
++++++++++++++++++

WopMars has been tested with three database engines: **SQLite**, **MySQL** and **PostgreSQL**. To run a workflow with these engines you will need a valid directory path for SQLite or existing databases and user for MySQL and PostgreSQL. Then you specifed the SQLAlchemy database URL in the wopmars option `D` as here.

.. code-block:: bash

    wopmars -D "sqlite:///output/db.sqlite"

.. code-block:: bash

    wopmars -D "mysql://wopuser:mypass@localhost/wopdb"

.. code-block:: bash

    wopmars -D "postgresql://wopuser:mypass@localhost/wopdb"


Options and arguments
+++++++++++++++++++++

-v --verbosity
    This option allows to set the verbosity of the logger. The more you add ``v`` after the dash, the more WopMars will be talkative. *Example*: ``wopmars -vv`` will output a lot of things because the level of logging will be set to debug. Usually, you'll use one to see the informations about the steps of execution.
   
-g --dot=FILE
    This option allows to specify a file where you want WopMars to write the ``.dot`` and ``.ps`` files giving a graphical representation of your workflow in ``pdf``.

-L --log=FILE
    This option allows to specify an other file than ``$HOME/.wopmars/wopmars.log`` to write the logs of the current execution. The logs are very important, if you have issues that you don't understand, you should try to run WopMars with ``-vv`` and send us your log file to help us figure out what is going on.

-p --printtools
    This option allows to actually display the output of WopMars in the Terminal, not only write it in the log file. You should use it sparingly, writing things at screen has an udge cost for your machine and can drastically lower your performances.

.. _sourcerule-label:

-f --sourcerule=RULE
    This option allows to say to WopMars from which rule you want to start the workflow. Each rule successing this one will be executed. 
    
.. figure::  ../images/from.png
   :align:   center
   
   *The tools executed are all the successors of the "source rule", here, rule 2. However, if output 1 is not available, this option will lead to an error*

-t --targetrule=RULE
    This option allows to say to WopMars to which rule you want the workflow to go to. Each rule predecessing this one will be executed.

.. figure::  ../images/to.png
   :align:   center
   
   *The tools executed are all the predecessors of the "target rule", here, rule 4*
    
-F --forceall=RULE
    This option allows to force WopMars to execute each rule it encounters during the workflow. Actualy, WoPMars try to execute the less possible tasks. Each time he encounters a rule that he thinks he has already executed in previous execution and he still has the result, he skips the rule. This option allows to denie this behavior.

-n --dry-run
    This option allows to simulate an execution. WopMars will behave like a normal execution except he won't execute anything. This can be used to prevent mistakes in long workflows without actually suffer the error.

-D --database=DATABASE
    This option allows to specify the database where you want WopMars to store the results. The default is ./wopmars.sqlite.

-w --wopfile=FILE
     This option allows to specifty the workflow definition file you want to use. The default is ./Wopfile

tool TOOLWRAPPER
    This command allows to run only one `Toolwrapper` without building the Wopfile. The Toolwrapper should be specified with its full name lgnome-tweak-toolike if you were calling it from the workflow definition file.

-i --input=DICT
    This option is used to specify the `inputs` when using the `tool` mode. It takes a String formated like a Python dictionnary with two levels of hierarchy. 
    - The first level allows to specify if it is an input 'file' or a 'table'.
    - The second level allows to specify the usual key-value couple like if you were building the Wopfile

-o --output=DICT
    This option is used to specify the `outputs` when using the `tool` mode. It takes a String formated like a Python dictionnary with two levels of hierarchy. 
    - The first level allows to specify if it is an output 'file' or a 'table'.
    - The second level allows to specify the usual key-value couple like if you were building the Wopfile

-P --params=DICT
    This option is used to specify the `params` when using the `tool` mode. It takes a String formated like a Python dictionnary with the usual key-value couple like if you were building the Wopfile

-c --clear-history
    This option is used when there is an error related to the history of WopMars. It allows to deleter all ``wom_`` like bases and start a new execution. Beware, even if a Tool shouldn't be re-executed, WopMars won't be able to say if it is right or not and then will re-execute every tools.

-l --toolwrapper-log
    This option will print the logs written by the toolwrapper developper. It shouldn't be used by the common user and has been created for debugging purposes. This log won't be stored in the log file.






























