"""
Module containing the Parser class
"""
import sys

from src.main.fr.tagc.wopmars.framework.management.DAG import DAG
from src.main.fr.tagc.wopmars.framework.parsing.Reader import Reader
from src.main.fr.tagc.wopmars.utils.Logger import Logger
from src.main.fr.tagc.wopmars.utils.OptionManager import OptionManager
from src.main.fr.tagc.wopmars.utils.exceptions.WopMarsException import WopMarsException

from networkx.algorithms.dag import is_directed_acyclic_graph


class Parser:
    """
    The Parser is used to organize the parsing of the Workflow Definition File.

    The aim of the Parser is to send the DAG representing the execution graph
    """
    def __init__(self, s_file_path):
        """
        The constructor of Parser.

        Initialize the reader with the definition_file path.
        
        :return:
        """

        self.__reader = Reader(s_file_path)

    def parse(self):
        """
        Organize the parsing of the Workflow Definition File

        Call the "read()" method of the reader to extract the set of objects of the workflow.
        Call the dag to build itself from the set of tools.

        If The "--dot" option is set, the dot file is wrote here.

        :raise: WopMarsParsingException if the workflow is not a DAG.
        :return: the DAG
        """

        set_toolwrappers = self.__reader.read()
        dag_tools = DAG(set_toolwrappers)
        if not is_directed_acyclic_graph(dag_tools):
            raise WopMarsException("Error while parsing the configuration file: \n\tThe workflow is malformed:",
                                   "The specified Workflow cannot be represented as a DAG.")
        s_dot_option = OptionManager()["--dot"]
        if s_dot_option:
            Logger.instance().info("Writing the dot and ps files representing the workflow...")
            dag_tools.write_dot(s_dot_option)
            Logger.instance().info("Dot and ps file wrote.")
        return dag_tools
