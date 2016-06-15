"""WopMars: Workflow Python Manager for Reproducible Science.

Usage:
  wopmars.py [-n] [-v...] [-d FILE] [-L FILE] [DEFINITION_FILE]

Arguments:
  DEFINITION_FILE  Path to the definition file of the workflow [default: wopfile.yml].

Options:
  -h --help           Show this help.
  -v                  Set verbosity level.
  -d FILE --dot=FILE  Write dot representing the workflow in the FILE file (with .dot extension).
  -L FILE --log=FILE  Write logs in FILE file [default: $HOME/.wopmars/wopmars.log].
  -n --noisy          Write logs in standard output.
"""
import os
import sys
import re

from docopt import docopt, DocoptExit
from schema import Schema, And, Or, Use, SchemaError

from src.main.fr.tagc.wopmars.framework.bdd.SQLManager import SQLManager
from src.main.fr.tagc.wopmars.framework.management.WorkflowManager import WorkflowManager
from src.main.fr.tagc.wopmars.utils.Logger import Logger
from src.main.fr.tagc.wopmars.utils.OptionManager import OptionManager
from src.main.fr.tagc.wopmars.utils.PathFinder import PathFinder
from src.main.fr.tagc.wopmars.utils.exceptions.WopMarsException import WopMarsException
# TODO faire en sorte que les imports commencent a fr


class WopMars:

    @staticmethod
    def run(argv):
        """
        Entry-point of the program
        """
        # if the command line is malformed, docopt interrupt the software.
        try:
            OptionManager(docopt(__doc__, argv=argv))
        except DocoptExit as SE:
            sys.exit("Bad argument in the command line.\n" + str(SE))

        try:
            schema_option = Schema({
                'DEFINITION_FILE': Or("wopfile.yml", Use(open)),
                '-v': Or(0, And(Use(int), lambda n: 1 < n < 5)),
                '--dot': Use(PathFinder.check_valid_path),
                "--log": Use(PathFinder.check_valid_path),
                '--noisy': Use(bool)
            })

            OptionManager().validate(schema_option)
        except SchemaError as schema_msg:
            Logger.instance().debug("\nCommand line Args:" + str(OptionManager()))
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
                Logger.instance().error("The option key " + match_wrong_key.group(1) + " is not known.")
            else:
                Logger.instance().error("An unknown error has occured. Message: " + str(schema_msg))
            sys.exit()

        Logger.instance().debug("\nCommand line Args:" + str(OptionManager()))

        try:
            wm = WorkflowManager()
            wm.run()
        except WopMarsException as WE:
            Logger.instance().error(str(WE))
            SQLManager.instance().get_session().rollback()
            sys.exit()

def main():
    sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/toolwrappers/")
    sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/base/")

    cmd_line_working = ["/home/giffon/Documents/wopmars/src/resources/example_def_file5.yml", "--dot", "/home/giffon/ex.dot", "-vvvv"]
    cmd_line_never_ready = ["/home/giffon/Documents/wopmars/src/resources/example_def_file_toolwrapper_never_ready.yml", "-vvvv"]
    cmd_line_error_parsing = ["/home/giffon/Documents/wopmars/src/resources/example_def_file_not_a_dag.yml", "-vvvv"]
    cmd_line_wrong_arg = ["/home/giffon/Documents/wopmars/src/resources/example_def_file_not_a_dag.yml", "--fail"]
    # WopMars.run(cmd_line_working)
    # WopMars().run(cmd_line_never_ready)
    # WopMars().run(cmd_line_error_parsing)
    # WopMars().run(cmd_line_wrong_arg)

    WopMars().run(sys.argv[1:])

if __name__ == "__main__":
    main()