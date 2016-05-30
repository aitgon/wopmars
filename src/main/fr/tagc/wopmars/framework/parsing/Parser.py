"""
Module containing the Parser class
"""
import sys

from fr.tagc.wopmars.framework.management.DAG import DAG
from fr.tagc.wopmars.framework.parsing.Reader import Reader
from fr.tagc.wopmars.utils.exceptions.WopMarsParsingException import WopMarsParsingException

from networkx.algorithms.dag import is_directed_acyclic_graph

class Parser:
    """
    The Parser is used to organize the parsing of the Workflow Definition File.

    The aim of the Parser is to send the DAG representing the execution graph
    """
    def __init__(self, path):
        """
        First line short documentation
        
        More documentation
        :return:
        """
        try:
            self.__reader = Reader(path)
        except WopMarsParsingException as e:
            print()
            sys.exit(str(e))

    def parse(self):
        """
        Organize the parsing of the Workflow Definition File

        Call the reader to extract the content and build the objects
        Call the dag to build itself

        :return: the DAG
        """
        try:
            set_toolwrappers = self.__reader.read()
            dag_tools = DAG(set_toolwrappers)
            if not is_directed_acyclic_graph(dag_tools):
                raise WopMarsParsingException(6, "")
            # todo loging
            print("Writing the dot file...", end="")
            # TODO faire une condition avec le optionmanager quand il sera crée
            dag_tools.write_dot("/home/giffon/dag.dot")
            # TODO loging
            print(" -> done.")
        except WopMarsParsingException as e:
            print()
            sys.exit(str(e))
        return dag_tools

if __name__ == '__main__':
    p = Parser("/home/giffon/Documents/wopmars/src/resources/example_def_file_not_a_dag.yml")
    p.parse()

    # opening the file
    import os

    os.system("dot -Tps /home/giffon/dag.dot -o /home/giffon/dag.ps; xdg-open /home/giffon/dag.ps")
