"""
Module containing the Parser class
"""
import sys

from src.main.fr.tagc.wopmars.framework.parsing.Reader import Reader
from src.main.fr.tagc.wopmars.utils.exceptions.WopMarsParsingException import WopMarsParsingException


class Parser:
    """
    The Parser is used to organize the parsing of the Workflow Definition File.

    The aim of the Parser is to send the DAG representing the execution graph
    """    
    def __init__(self):
        """
        First line short documentation
        
        More documentation
        :return:
        """
        # TODO fill the constructor of parser

    def parse(self, path):
        """
        Organize the parsing of the Workflow Definition File

        Call the reader to extract the content and build the objects
        Call the dag to build itself

        :return: the DAG
        """
        try:
            my_reader = Reader(path)
            set_toolwrappers = my_reader.read()
        except WopMarsParsingException as e:
            sys.exit(e)
        # TODO fill the method parse

if __name__ == '__main__':
    p = Parser()
    p.parse("/home/giffon/Documents/WopMars/projet/src/resources/example_def_file.yml")