"""
Module containing the WorkflowManager class
"""
from queue import Queue

import copy

from fr.tagc.wopmars.framework.parsing.Parser import Parser
from fr.tagc.wopmars.framework.management.ToolWrapperObserver import ToolWrapperObserver
from fr.tagc.wopmars.utils.Logger import Logger

from fr.tagc.wopmars.utils.OptionManager import OptionManager

class WorkflowManager(ToolWrapperObserver):
    """
    The WorkflowManager class manage all the software execution.

    He will ask the parser to build the DAG then execute it.
    """    
    def __init__(self):
        """
        First line short documentation
        
        More documentation
        :param something:
        :return:
        """
        self.__parser = Parser(OptionManager()["DEFINITION_FILE"])
        self.__queue_exec = Queue()
        self.__dag_tools = None

    #todo ask lionel en testant cette méthode, je teste tout, non?
    def run(self):
        """
        Get the dag then execute it
        :return:
        """
        self.__dag_tools = self.__parser.parse()
        # start at the begining of the dag
        self.execute_from()

    def execute_from(self, node=None):
        """
        Execute the dag.

        :param node: ToolWrapper a node of the DAG
        :return: void
        """

        list_tw = self.__dag_tools.successors(node)
        # all origin elements are in queue
        for tw in list_tw:
            self.__queue_exec.put(tw)

        self.run_queue()

    def run_queue(self):
        """
        Call start() method of all elements of the queue

        :return: void
        """
        int_queue_size_ini = self.__queue_exec.qsize()
        index = 0
        # todo tests unitaires poussés
        while index < int_queue_size_ini and not self.__queue_exec.empty():
            tw = self.__queue_exec.get()
            tw.subscribe(self)
            tw.start()
            index += 1

    def notify_success(self, toolwrapper):
        """
        Handle toolwrapper success by continuing the dag.

        Implementation of the super class method.
        :param toolwrapper: ToolWrapper that just succeed
        :return:
        """
        Logger().info(str(toolwrapper.__class__.__name__) + " has succeed.")
        # Continue the dag execution from the toolwrapper that just finished.
        self.execute_from(toolwrapper)

    def notify_failure(self, toolwrapper):
        """
        Handle toolwrapper failure by re-puting it in the queue.

        :param toolwrapper: ToolWrapper that just failed
        :return:
        """
        # todo gérer le fait de ne pas boucler à l'infini
        Logger().info(str(toolwrapper.__class__.__name__) + " has failed.")
        self.__queue_exec.put(toolwrapper)

if __name__ == "__main__":
    my_workflow = WorkflowManager()
    my_workflow.run()
