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
from docopt import docopt

from fr.tagc.wopmars.framework.parsing.Parser import Parser
from fr.tagc.wopmars.utils.OptionManager import OptionManager


class WopMars:
    def __init__(self):
        self.__s_workflow_definition_filename = "path/to/the/file"

    def run(self):
        """
        Entry-point of the program
        """
        option_manager = OptionManager(docopt(__doc__))
        print(option_manager)

        # parser = Parser()
        # parser.parse()


if __name__ == "__main__":
    WopMars().run()
