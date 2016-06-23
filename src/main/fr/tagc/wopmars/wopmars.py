"""WopMars: Workflow Python Manager for Reproducible Science.

Usage:
  wopmars.py [-n] [-p] [-F] [-v...] [-d FILE] [-L FILE] [-f RULE | -t RULE] [DEFINITION_FILE] [DATABASE]

Arguments:
  DEFINITION_FILE  Path to the definition file of the workflow [default: wopfile.yml].
  DATABASE         Path to the sqlite database file [default: $HOME/.wopmars/db.sqlite]

Options:
  -h --help                    Show this help.
  -v                           Set verbosity level.
  -d FILE --dot=FILE           Write dot representing the workflow in the FILE file (with .dot extension).
  -L FILE --log=FILE           Write logs in FILE file [default: $HOME/.wopmars/wopmars.log].
  -p --printtools              Write logs in standard output.
  -f RULE --sourcerule=RULE    Execute the workflow from the given RULE.
  -t RULE --targetrule=RULE    Execute the workflow to the given RULE.
  -F --forceall                Force the execution of the workflow, without checking for previous executions.
  -n --dry                     Do not execute anything but simulate.
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
# todo parcourir le code pour refaire la documentation -> compatible sphinx
# todo faire plus de tests: notamment pour la partie "from" et "to"
# todo parcourir l'exécution du code pour améliorer les messages de Log... bien réfléchir à ce qui est import, penser
# aux garde - fou
# todo verifier attentivement la trace par rapport a la base de données, je pense qu'il peut y avoir un bug sachant que
# le test d'existence des resultats repose sur le fait que la table soit vide ou pas: deux cas de figure qui posent probleme:
#    - si un outil a une table comme input et la meme table comme output, alors sa date d'utilisation comme input sera 1,
#      comme output sera 2, nouvel input = 2 donc on s'en sert pas -> c'est ok
#    - si un outil a une table comme input et la meme table comme output et qu'un autre outil arrive après lui avec la meme table comme input,
#      dans ce cas, le workflow ne peut pas savoir quel outil doit arriver en premier !!! todo ask aitor todo ask lionel


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
            sys.exit("Bad argument in the command line: \n\t" + " ".join(argv) + "\n" + str(SE))

        try:
            schema_option = Schema({
                'DEFINITION_FILE': Or("wopfile.yml", Use(lambda k: open(k).close())),
                'DATABASE': Use(PathFinder.check_valid_path),
                '-v': Or(0, And(int, lambda n: 1 < n < 5)),
                '--dot': Use(PathFinder.check_valid_path),
                "--log": Use(PathFinder.check_valid_path),
                '--printtools': Use(bool),
                "--sourcerule": Or(None, str),
                "--targetrule": Or(None, str),
                "--forceall": Use(bool),
                "--dry": Use(bool)
            })
            # The option values are validated using schema library
            OptionManager.instance().validate(schema_option)
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
                Logger.instance().error("The option key " + match_wrong_key.group(1) + " is not known.")
            else:
                Logger.instance().error("An unknown error has occured. Message: " + str(schema_msg))
            sys.exit(1)

        Logger.instance().debug("\nCommand line Args:" + str(OptionManager.instance()))

        try:
            wm = WorkflowManager()
            wm.run()
        except WopMarsException as WE:
            Logger.instance().error(str(WE))
            SQLManager.instance().get_session().rollback()
            sys.exit(1)


def main():
    sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/toolwrappers/")
    sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/base/")

    l = ["python",  "/home/giffon/Documents/wopmars/src/resources/example_def_file2.yml", "--dot", "/home/giffon/wopmars.dot", "-n", "-vvvv"]

    WopMars().run(sys.argv)
    # WopMars().run(l)

if __name__ == "__main__":
    main()
