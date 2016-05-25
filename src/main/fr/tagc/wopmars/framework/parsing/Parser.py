"""
Module containing the Parser class
"""
import sys

from src.main.fr.tagc.wopmars.framework.management.DAG import DAG
from src.main.fr.tagc.wopmars.framework.parsing.Reader import Reader
from src.main.fr.tagc.wopmars.utils.exceptions.WopMarsParsingException import WopMarsParsingException


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
        self.__reader = Reader(path)

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
        except WopMarsParsingException as e:
            sys.exit(str(e))
        return dag_tools
        # TODO fill the method parse

if __name__ == '__main__':
    p = Parser("/home/giffon/Documents/wopmars/src/resources/example_def_file2.yml")
    p.parse()