"""WopMars: Workflow Python Manager for Reproducible Science.

Usage:
  wopmars (-D DATABASE) (-w DEFINITION_FILE) [-n] [-p] [-F] [-v...] [-d DIR] [-g FILE] [-L FILE] [-f RULE | -t RULE] [-c] [-l]
  wopmars tool TOOLWRAPPER [-i DICT] [-o DICT] [-P DICT] [-p] [-F] [-D DATABASE] [-v...] [-d DIR] [-L FILE] [-g FILE] [-c] [-l]
  wopmars example [-d DIR]
  wopmars example_snp [-d DIR]

Arguments:
  DEFINITION_FILE  Path to the definition file of the workflow (Required)
  DATABASE         Path to the sqlite database file (Required)
  FILE             Path to a file.
  RULE             Name of a rule in the workflow definition file.
  TOOLWRAPPER      Path the the toolwrapper
  DICT             String formated like a dictionnary. Ex: "{'input1': 'path/to/input1', 'input2': 'path/to/input2'}"

Options:
  -D --database=DATABASE       REQUIRED: Set the path to the database, e.g -D sqlite:///db.sqlite
  -w --wopfile=DEFINITION_FILE REQUIRED: Set the path to the definition file.
  -c --clear-history           Clear WoPMaRS history. Should be used in case of bug which seem to be related to the history. Be carefull, clearing history will result in a re-execution of the whole workflow.
  -d --directory=DIR           Set the current working directory. Useful for working with relative paths [default: $CWD].
  -F --forceall                Force the execution of the workflow, without checking for previous executions.
  -f RULE --sourcerule=RULE    Execute the workflow from the given RULE.
  -g FILE --dot=FILE           Write dot representing the workflow in the FILE file (with .dot extension). This option needs to install WopMars with pygraphviz (pip install wopmars[pygraphviz])
  -h --help                    Show this help.
  -i --input=DICT              Set the input of the toolwrapper you want to use in the dictionnary format.
  -l --toolwrapper-log         Allow the toolwrapper to print its logs in the standard output.
  -L FILE --log=FILE           Write logs in FILE file [default: $HOME/.wopmars/wopmars.log].
  -n --dry-run                 Only display what would have been done.
  -o --output=DICT             Set the output of the toolwrapper you want to use in the dictionnary format.
  -P --params=DICT             Set the parameters of the toolwrapper you want to use in the dictionnary format.
  -p --printtools              Write logs in standard output.
  -t RULE --targetrule=RULE    Execute the workflow to the given RULE.
  -u --update                  Should be used when a file supposedly generated by the workflow already exists and should be used as it. (Not implemented)
  -v                           Set verbosity level, eg -v, -vv or -vvv

Example:
    wopmars example
    cd wopmars_example
    pip install .
    wopmars -w Wopfile -D "sqlite:///db.sqlite" -v -p -F
"""

import os
import re
import sys

from docopt import docopt, DocoptExit
from schema import Schema, And, Or, Use, SchemaError

from wopmars.example.ExampleBuilder import ExampleBuilder
from wopmars.SQLManager import SQLManager
from wopmars.WorkflowManager import WorkflowManager
from wopmars.utils.DictUtils import DictUtils
from wopmars.utils.Logger import Logger
from wopmars.utils.OptionManager import OptionManager
from wopmars.utils.PathFinder import PathFinder
from wopmars.utils.exceptions.WopMarsException import WopMarsException
from wopmars.constants import home_wopmars
from wopmars.utils.various import time_unix_ms

# todo combinatorices pour les rules
# todo option pour reset les resultats (supprimer le contenu de la database) / fresh run
# todo ajouter un flag NOT_FINISHED aux executions

__version__='0.0.2'

class WopMars:

    @staticmethod
    def run(argv):
        """
        Entry-point of the program
        """

        # if the command line is malformed, docopt interrupt the software.
        try:
            if argv[1:] == []: # If not arguments, run the help
                argv.append('-h')
            OptionManager.instance().update(docopt(__doc__, argv=argv[1:]))
        except DocoptExit as SE:
            print("Bad argument in the command line: \n\t" + " ".join(argv) + "\n" + str(SE))
            sys.exit(2)
        try:
            schema_option = Schema({
                '--wopfile': Or("Wopfile", str),
                '--database': Use(PathFinder.check_database_valid_url),
                '-v': Or(0, And(int, lambda n: 1 <= n <= 2)),
                '--dot': Or(None, And(Use(PathFinder.check_valid_path), Use(PathFinder.check_pygraphviz))),
                "--log": Use(PathFinder.check_valid_path),
                '--printtools': Use(bool),
                "--sourcerule": Or(None, str),
                "--targetrule": Or(None, str),
                "--forceall": Use(bool),
                "--dry-run": Use(bool),
                "--directory": Use(PathFinder.create_workingdir),
                "--input": Use(DictUtils.str_to_dict),
                "--output": Use(DictUtils.str_to_dict),
                "--params": Use(DictUtils.str_to_dict),
                "TOOLWRAPPER": Or(None, Use(PathFinder.is_in_python_path)),
                "tool": Use(bool),
                "example": Use(bool),
                "example_snp": Use(bool),
                "--clear-history": Use(bool),
                "--toolwrapper-log": Use(bool)
            })
            # The option values are validated using schema library
            OptionManager.instance().validate(schema_option)
            os.chdir(OptionManager.instance()["--directory"])
        except SchemaError as schema_msg:
            Logger.instance().debug("\nCommand line Args:" + str(OptionManager.instance()))
            # regex for the different possible error messages.
            match_open_def = re.match(r"^open\('(.[^\)]+)'\)", str(schema_msg))
            match_dot_def = re.match(r"^check_valid_path\(('.[^\)]+')\)", str(schema_msg))
            match_wrong_key = re.match(r"^Wrong keys ('.[^\)]+')", str(schema_msg))
            match_pygraphviz = re.match(r".*dot.*", str(schema_msg))
            print(match_pygraphviz)
            # Check the different regex..
            if match_open_def:
                Logger.instance().error("The file " + match_open_def.group(1) + " cannot be opened. It may not exist.")
            elif match_dot_def:
                Logger.instance().error("The path " + match_dot_def.group(1) + " is not valid.")
            elif match_wrong_key:
                # Normally never reach
                Logger.instance().error("The option key " + match_wrong_key.group(1) + " is not known.")
            elif match_pygraphviz:
                Logger.instance().error("The dot file path is not valid or the pygraphviz module is not installed. In the second case, install wopmars with pygraphviz: pip install wopmars[pygraphviz]")
            else:
                # Normally never reach
                Logger.instance().error("An unknown error has occured. Message: " + str(schema_msg))
            sys.exit(2)

        Logger.instance().debug("\nCommand line Args:" + str(OptionManager.instance()))

        if OptionManager.instance()["example"]:
            ExampleBuilder().build()
            sys.exit(1)

        if OptionManager.instance()["example_snp"]:
            ExampleBuilder().build_snp()
            sys.exit(1)


        wm = WorkflowManager()
        try:
            wm.run()
        except WopMarsException as WE:
            Logger.instance().error(str(WE))
            session = SQLManager.instance().get_session()
            try:
                finished_at = time_unix_ms()
                Logger.instance().error("The workflow has encountered an error at: " + str(finished_at))
                wm.set_finishing_informations(finished_at, "ERROR")
            except AttributeError:
                session.rollback()
                Logger.instance().error("The execution has not even begun. No informations will be stored in the database.")
            except Exception as e:
                Logger.instance().error("An error occured during the rollback of the changement of the database which can be now unstable:" +
                                        str(e))
            sys.exit(1)
        # except Exception as e:
        #     Logger.instance().error("An unknown error has occured:\n" + str(e))
        #     sys.exit(1)


def run():
    # todo ask lionel: du coup, ça, c'est pas censé y être? vu que les toolwrappers ne devront pas être dans
    # l'arborescence du projet? même les toolwrappers de base
    sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/toolwrappers/")
    sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/base/")



    if not os.path.isdir(home_wopmars):
        os.makedirs(home_wopmars)

    WopMars().run(sys.argv)

if __name__ == "__main__":
    run()
