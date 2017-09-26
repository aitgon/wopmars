"""
Module containing the Parser class
"""
import sys

from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql.functions import func

from wopmars.framework.database.SQLManager import SQLManager
from wopmars.framework.database.tables.Execution import Execution
from wopmars.framework.database.tables.ToolWrapper import ToolWrapper
from wopmars.framework.management.DAG import DAG
from wopmars.framework.parsing.Reader import Reader
from wopmars.utils.Logger import Logger
from wopmars.utils.OptionManager import OptionManager
from wopmars.utils.exceptions.WopMarsException import WopMarsException

from networkx.algorithms.dag import is_directed_acyclic_graph


class Parser:
    """
    The Parser is used to organize the parsing of the Workflow Definition File.

    The aim of the Parser is to send the DAG representing the execution graph.
    """
    def __init__(self):
        """
        The constructor of Parser.

        Initialize the reader.
        
        :return:
        """
        self.__reader = Reader()

    def parse(self):
        """
        Organize the parsing of the Workflow Definition File or the Tool if only one tool is provided thanks to the
        tool command.

        Call the "read()" or the "load_one_toolwrapper" (depending on the use or not of tool command) method of the
        reader to insert in database the set of objects of the workflow.

        Then, the toolwrappers of the last execution are got back before calling the dag to build itself from the set of tools.

        The DAG is checked to actually being a Directed Acyclic Graph.

        If The "--dot" option is set, the dot and ps file are wrote here.

        :raise: WopMarsParsingException if the workflow is not a DAG.
        :return: the DAG
        """
        if not OptionManager.instance()["tool"]:
            self.__reader.read(OptionManager.instance()["--wopfile"])
        else:
            self.__reader.load_one_toolwrapper(OptionManager.instance()["TOOLWRAPPER"],
                                               OptionManager.instance()["--input"],
                                               OptionManager.instance()["--output"],
                                               OptionManager.instance()["--params"])
        # Get back the set of toolwrappers of the workflow before executing them.
        set_toolwrappers = self.get_set_toolwrappers()
        dag_tools = DAG(set_toolwrappers)
        if not is_directed_acyclic_graph(dag_tools):
            # todo find out the loop to specify it in the error message
            raise WopMarsException("Error while parsing the configuration file: \n\tThe workflow is malformed:",
                                   "The specified Workflow cannot be represented as a DAG.")
        s_dot_option = OptionManager.instance()["--dot"]
        if s_dot_option:
            Logger.instance().info("Writing the dot and ps files representing the workflow at " + str(s_dot_option))
            dag_tools.write_dot(s_dot_option)
            Logger.instance().debug("Dot and ps file wrote.")
        return dag_tools

    @staticmethod
    def get_set_toolwrappers():
        """
        Ask the database for toolwrappers of the current execution.

        The current execution is defined as the one with the highest id (it is auto_incrementing)

        :return: Set([ToolWrapper]) the set of toolwrappers of the current execution.
        """
        session = SQLManager.instance().get_session()
        set_toolwrappers = set()
        try:
            # query asking the db for the highest execution id
            execution_id = session.query(func.max(ToolWrapper.execution_id))
            Logger.instance().debug("Getting toolwrappers of the current execution. id = " + str(execution_id.one()[0]))
            set_toolwrappers = set(session.query(ToolWrapper).filter(ToolWrapper.execution_id == execution_id).all())
        except NoResultFound as e:
            raise e
        return set_toolwrappers
