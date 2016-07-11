"""WopMars: Workflow Python Manager for Reproducible Science.

Usage:
  wopmars.py [-n] [-p] [-F] [-v...] [-d DIR] [-g FILE] [-L FILE] [-f RULE | -t RULE] [-D DATABASE] [-w DEFINITION_FILE]
  wopmars.py tool TOOLWRAPPER [-i DICT] [-o DICT] [-P DICT] [-p] [-F] [-v...]

Arguments:
  DEFINITION_FILE  Path to the definition file of the workflow [default: wopfile.yml].
  DATABASE         Path to the sqlite database file [default: $HOME/.wopmars/db.sqlite]
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
  -n --dry                     Do not execute anything but simulate.
  -d --directory=DIR           Set the current working directory. Usefull for working with relative poths [default: $CWD].
  -D --database=DATABASE       Set the path to the database.
  -w --wopfile=DEFINITION_FILE Set the path to the definition file.
  -i --input=DICT              Set the input of the toolwrapper you want to use in the dictionnary format.
  -o --output=DICT             Set the output of the toolwrapper you want to use in the dictionnary format.
  -P --params=DICT             Set the parameters of the toolwrapper you want to use in the dictionnary format.
"""
import os
import sys
import re

from docopt import docopt, DocoptExit
from schema import Schema, And, Or, Use, SchemaError

from src.main.fr.tagc.wopmars.framework.bdd.SQLManager import SQLManager
from src.main.fr.tagc.wopmars.framework.management.WorkflowManager import WorkflowManager
from src.main.fr.tagc.wopmars.utils.DictUtils import DictUtils
from src.main.fr.tagc.wopmars.utils.Logger import Logger
from src.main.fr.tagc.wopmars.utils.OptionManager import OptionManager
from src.main.fr.tagc.wopmars.utils.PathFinder import PathFinder
from src.main.fr.tagc.wopmars.utils.exceptions.WopMarsException import WopMarsException
# TODO faire en sorte que les imports commencent a fr
# todo parcourir le code pour refaire la documentation -> compatible sphinx
# todo specifier l'exception de "non dag" pour dire entre quels outils apparait le cycle


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
                '--wopfile': Or("wopfile.yml", str),
                '--database': Use(PathFinder.check_valid_path),
                '-v': Or(0, And(int, lambda n: 1 < n < 5)),
                '--dot': Use(PathFinder.check_valid_path),
                "--log": Use(PathFinder.check_valid_path),
                '--printtools': Use(bool),
                "--sourcerule": Or(None, str),
                "--targetrule": Or(None, str),
                "--forceall": Use(bool),
                "--dry": Use(bool),
                "--directory": Use(os.path.isdir),
                "--input": Use(DictUtils.str_to_dict),
                "--output": Use(DictUtils.str_to_dict),
                "--params": Use(DictUtils.str_to_dict),
                "TOOLWRAPPER": Or(None, Use(PathFinder.is_in_python_path)),
                "tool": Use(bool)
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

            # Check the different regex..
            if match_open_def:
                Logger.instance().error("The file " + match_open_def.group(1) + " cannot be opened. It may not exist.")
            elif match_dot_def:
                Logger.instance().error("The path " + match_dot_def.group(1) + " is not valid.")
            elif match_wrong_key:
                # Normally never reach
                Logger.instance().error("The option key " + match_wrong_key.group(1) + " is not known.")
            else:
                # Normally never reach
                Logger.instance().error("An unknown error has occured. Message: " + str(schema_msg))
            sys.exit(2)

        Logger.instance().debug("\nCommand line Args:" + str(OptionManager.instance()))

        try:
            wm = WorkflowManager()
            wm.run()
        except WopMarsException as WE:
            Logger.instance().error(str(WE))
            SQLManager.instance().get_session().rollback()
            sys.exit(1)


def main():
    # todo ask lionel: du coup, ça, c'est pas censé y être? vu que les toolwrappers ne devront pas être dans
    # l'arborescence du projet? même les toolwrappers de base
    sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/toolwrappers/")
    sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/base/")

    home_wopmars = os.path.join(os.path.expanduser("~"), ".wopmars/")

    if not os.path.isdir(home_wopmars):
        os.makedirs(home_wopmars)

    l = ["python",  "/home/luc/Documents/WORK/wopmars/src/resources/example_def_file.yml", "--dot", "~/.wopmars/wopmars.dot",
         "-p", "-vvvv", "-d", "/home/luc/Documents/WORK/wopmars/src"]
    WopMars().run(sys.argv)
    # WopMars().run(l)

if __name__ == "__main__":
    main()
