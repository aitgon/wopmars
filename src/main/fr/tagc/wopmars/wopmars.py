"""WopMars: Workflow Python Manager for Reproducible Science.

Usage:
  wopmars.py [-v...] DEFINITION_FILE

Arguments:
  DEFINITION_FILE  Path to the definition file of the workflow.

Options:
  -h --help     Show this help.
  --version     Show version.
  -v            Set verbosity level.
"""
import sys

from docopt import docopt
from schema import Schema, And, Or, Use, SchemaError

from fr.tagc.wopmars.framework.management.WorkflowManager import WorkflowManager
from fr.tagc.wopmars.utils.OptionManager import OptionManager


class WopMars:
    def __init__(self):
        self.__s_workflow_definition_filename = "path/to/the/file"

    def run(self):
        """
        Entry-point of the program
        """
        # , error='Invalid year'
        try:
            schema_option = Schema({
                # todo ask lionel est-ce-que les message sont assez clairs?
                'DEFINITION_FILE': Use(open, error='The definition file is not readable. The path may not exists.'),
                '-v': Or(0, And(Use(int), lambda n: 0 < n < 4))
            }, ignore_extra_keys=True)

            # si la ligne de commande est mal faite, docopt interrompt le tout
            dict_options = schema_option.validate(docopt(__doc__))
            OptionManager(dict_options)
        except SchemaError as schema_msg:
            # todo ask lionel est-ce-que les message sont assez clairs?
            sys.exit(schema_msg)

        wm = WorkflowManager()
        wm.run()

if __name__ == "__main__":
    WopMars().run()
