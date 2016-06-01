"""
Module containing the WorkflowManager class
"""
from queue import Queue

import copy

import sys

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
        self.__list_queue_buffer = []
        self.__count_exec = 0
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
        Logger().debug("Next tools: " + str([t.__class__.__name__ for t in list_tw]))
        # all origin elements are in queue
        for tw in list_tw:
            self.__queue_exec.put(tw)

        self.run_queue()

    def run_queue(self):
        """
        Call start() method of all elements of the queue

        :return: void
        """
        # int_queue_size_ini = self.__queue_exec.qsize()
        # index = 0
        # # todo tests unitaires poussés
        # while index < int_queue_size_ini and not self.__queue_exec.empty():
        #     tw = self.__queue_exec.get()
        #     tw.subscribe(self)
        #     tw.start()
        #     index += 1

        ######
        while not self.__queue_exec.empty():
            Logger().debug("Queue size: " + str(self.__queue_exec.qsize()))
            tw = self.__queue_exec.get()
            if tw.are_inputs_ready():
                Logger().debug("ToolWrapper ready: " + str(tw.__class__.__name__))
                # todo verification des ressources
                tw.subscribe(self)
                self.__count_exec += 1
                tw.start()
            else:
                Logger().debug("ToolWrapper not ready: " + str(tw.__class__.__name__))
                self.__list_queue_buffer.append(tw)

        Logger().debug("Buffer: " + str([t.__class__.__name__ for t in self.__list_queue_buffer]))
        Logger().debug("Running ToolWrappers: " + str(self.__count_exec))

        if self.__count_exec == 0:
            if len(self.__list_queue_buffer) == 0:
                Logger().info("The workflow has completed.")
                sys.exit()
            elif not self.check_buffer():
                # todo throw exception?
                Logger().error("The workflow has failed. The inputs are not ready for the remaining tools: " +
                               ", ".join([t.__class__.__name__ for t in self.__list_queue_buffer]) + ". ")
                sys.exit()

    def check_buffer(self):
        for tw in self.__list_queue_buffer:
            # todo enum_type
            if tw.get_state() == "READY":
                return True
        return False

    def notify_success(self, toolwrapper):
        """
        Handle toolwrapper success by continuing the dag.

        Implementation of the super class method.
        :param toolwrapper: ToolWrapper that just succeed
        :return:
        """
        Logger().info(str(toolwrapper.__class__.__name__) + " has succeed.")
        # Continue the dag execution from the toolwrapper that just finished.
        self.__count_exec -= 1
        self.execute_from(toolwrapper)

    def notify_failure(self, toolwrapper):
        """
        Handle toolwrapper failure by re-puting it in the queue.

        :param toolwrapper: ToolWrapper that just failed
        :return:
        """
        # todo n'est jamais atteint
        # todo gérer le fait de ne pas boucler à l'infini
        Logger().info(str(toolwrapper.__class__.__name__) + " has failed.")
        self.__count_exec -= 1
        self.__queue_exec.put(toolwrapper)

if __name__ == "__main__":
    my_workflow = WorkflowManager()
    my_workflow.run()
