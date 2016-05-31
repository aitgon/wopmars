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
import os

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
        try:
            # todo trouver une solution pour rendre les messages plus explicites
            schema_option = Schema({
                # todo ask lionel est-ce-que les message sont assez clairs? je suppose que non...
                'DEFINITION_FILE': Use(open, error='The definition file is not readable. The path may not exists.'),
                '-v': Or(0, And(Use(int), lambda n: 1 < n < 4)),
                '--dot': Use(PathFinder.check_valid_path, error='The destination path for dot file is not valid')
            })
            # if the command line is malformed, docopt interrupt the software.
            dict_options = schema_option.validate(docopt(__doc__, argv=argv))
            OptionManager(dict_options)
        except SchemaError as schema_msg:
            # todo ask lionel afficher de la couleur dans la console?
            Logger().error(schema_msg)
            sys.exit()

        Logger().debug(dict_options)

        wm = WorkflowManager()
        wm.run()

if __name__ == "__main__":
    WopMars().run(sys.argv[1:])
