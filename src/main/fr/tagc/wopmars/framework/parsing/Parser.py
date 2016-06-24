"""
Module containing the Parser class
"""
import sys

from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql.functions import func

from src.main.fr.tagc.wopmars.framework.bdd.SQLManager import SQLManager
from src.main.fr.tagc.wopmars.framework.bdd.tables.Execution import Execution
from src.main.fr.tagc.wopmars.framework.bdd.tables.ToolWrapper import ToolWrapper
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

        The DAG is checked to actually being a Directed Acyclic Graph.

        If The "--dot" option is set, the dot and ps file is wrote here.

        :raise: WopMarsParsingException if the workflow is not a DAG.
        :return: the DAG
        """
        self.__reader.read()
        set_toolwrappers = self.get_set_toolwrappers()
        dag_tools = DAG(set_toolwrappers)
        if not is_directed_acyclic_graph(dag_tools):
            raise WopMarsException("Error while parsing the configuration file: \n\tThe workflow is malformed:",
                                   "The specified Workflow cannot be represented as a DAG.")
        s_dot_option = OptionManager.instance()["--dot"]
        if s_dot_option:
            Logger.instance().info("Writing the dot and ps files representing the workflow at " + str(s_dot_option))
            dag_tools.write_dot(s_dot_option)
            Logger.instance().info("Dot and ps file wrote.")
        return dag_tools

    @staticmethod
    def get_set_toolwrappers():
        """
        Ask the bdd for toolwrappers of the current execution.

        The current execution is defined as the one with the highest id (it is auto_incrementing)

        :return: Set([ToolWrapper]) the set of toolwrappers of the current execution.
        """
        session = SQLManager.instance().get_session()
        set_toolwrappers = set([])
        try:
            execution_id = session.query(func.max(ToolWrapper.execution_id))
            Logger.instance().debug("Getting toolwrappers of the current execution. id = " + str(execution_id.one()[0]))
            set_toolwrappers = set(session.query(ToolWrapper).filter(ToolWrapper.execution_id == execution_id).all())
        except NoResultFound as e:
            raise WopMarsException("Error while parsing the configuration file. No execution have been found.",
                                   "It looks like the read has not returned any new execution")
        return set_toolwrappers
