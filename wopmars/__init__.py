"""WopMars: Workflow Python Manager for Reproducible Science.

Usage:
  wopmars [-n] [-p] [-F] [-v...] [-d DIR] [-g FILE] [-L FILE] [-f RULE | -t RULE] [-D DATABASE] [-w DEFINITION_FILE] [-c] [-l]
  wopmars tool TOOLWRAPPER [-i DICT] [-o DICT] [-P DICT] [-p] [-F] [-D DATABASE] [-v...] [-d DIR] [-L FILE] [-g FILE] [-c] [-l]
  wopmars example [-d DIR]
  wopmars example_snp [-d DIR]

Arguments:
  DEFINITION_FILE  Path to the definition file of the workflow [default: Wopfile].
  DATABASE         Path to the sqlite database file [default: wopmars.sqlite].
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
  -c --clear-history           Clear WoPMaRS history. Should be used in case of bug which seem to be related to the history. Be carefull, clearing history will result in a re-execution of the whole workflow.
  -u --update                  Should be used when a file supposedly generated by the workflow already exists and should be used as it. (Not implemented)
  -l --toolwrapper-log         Allow the toolwrapper to print its logs in the standard output.
"""
import datetime
import os
import re
import sys
import time

from docopt import docopt, DocoptExit
from schema import Schema, And, Or, Use, SchemaError

from wopmars.example.ExampleBuilder import ExampleBuilder
from wopmars.framework.database.SQLManager import SQLManager
from wopmars.framework.management.WorkflowManager import WorkflowManager
from wopmars.utils.DictUtils import DictUtils
from wopmars.utils.Logger import Logger
from wopmars.utils.OptionManager import OptionManager
from wopmars.utils.PathFinder import PathFinder
from wopmars.utils.exceptions.WopMarsException import WopMarsException

# todo combinatoire pour les rules
# todo option pour reset les resultats (supprimer le contenu de la database) / fresh run
# todo ajouter un flag NOT_FINISHED aux executions


class WopMars:

    @staticmethod
    def run(argv):
        """
        Entry-point of the program
        """

        # if the command line is malformed, docopt interrupt the software.
        try:
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
            match_pygraphviz = re.match(r".*pygraphviz.*", str(schema_msg))

            # Check the different regex..
            if match_open_def:
                Logger.instance().error("The file " + match_open_def.group(1) + " cannot be opened. It may not exist.")
            elif match_dot_def:
                Logger.instance().error("The path " + match_dot_def.group(1) + " is not valid.")
            elif match_wrong_key:
                # Normally never reach
                Logger.instance().error("The option key " + match_wrong_key.group(1) + " is not known.")
            elif match_pygraphviz:
                Logger.instance().error("The pygraphviz module is not installed, try installing WoPMaRS again without the 'no-pygraphviz' option.\n\t python3 setup.py install")
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
                finished_at = datetime.datetime.fromtimestamp(time.time())
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

    home_wopmars = os.path.join(os.path.expanduser("~"), ".wopmars/")

    if not os.path.isdir(home_wopmars):
        os.makedirs(home_wopmars)

    WopMars().run(sys.argv)

if __name__ == "__main__":
    run()
