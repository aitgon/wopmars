"""WopMars: Workflow Python Manager for Reproducible Science.

Usage:
  wopmars.py [-v...] [-d FILE] DEFINITION_FILE

Arguments:
  DEFINITION_FILE  Path to the definition file of the workflow.

Options:
  -h --help           Show this help.
  --version           Show version.
  -v                  Set verbosity level.
  -d FILE --dot=FILE  Write dot file (with .dot extension).
"""
import sys
import re

from docopt import docopt
from schema import Schema, And, Or, Use, SchemaError

from fr.tagc.wopmars.framework.management.WorkflowManager import WorkflowManager
from fr.tagc.wopmars.utils.Logger import Logger
from fr.tagc.wopmars.utils.OptionManager import OptionManager
from fr.tagc.wopmars.utils.PathFinder import PathFinder


class WopMars:
    def __init__(self):
        self.__s_workflow_definition_filename = "path/to/the/file"

    def run(self, argv):
        """
        Entry-point of the program
        """
        # if the command line is malformed, docopt interrupt the software.
        dict_options = OptionManager(docopt(__doc__, argv=argv))
        try:
            schema_option = Schema({
                'DEFINITION_FILE': Use(open),
                '-v': Or(0, And(Use(int), lambda n: 1 < n < 5)),
                '--dot': Use(PathFinder.check_valid_path)
            })

            OptionManager().validate(schema_option)
        except SchemaError as schema_msg:
            match_open_def = re.match(r"^open\('(.[^\)]+)'\)", str(schema_msg))
            match_dot_def = re.match(r"^check_valid_path\(('.[^\)]+')\)", str(schema_msg))

            if match_open_def:
                Logger().error("The file " + match_open_def.group(1) + " cannot be opened. It may not exist.")
            elif match_dot_def:
                Logger().error("The path " + match_dot_def.group(1) + " is not valid.")
            sys.exit()

        Logger().debug("Command line Args:" + str(dict_options))

        wm = WorkflowManager()
        wm.run()

if __name__ == "__main__":
    WopMars().run(sys.argv[1:])
    # WopMars().run(["", "/home/giffon/Documents/wopmars/src/resources/example_def_file3.yml"])
