"""
Module containing the WorkflowManager class
"""
import sys

from src.main.fr.tagc.wopmars.framework.management.ToolThread import ToolThread
from src.main.fr.tagc.wopmars.utils.UniqueQueue import UniqueQueue
from src.main.fr.tagc.wopmars.framework.parsing.Parser import Parser
from src.main.fr.tagc.wopmars.framework.management.ToolWrapperObserver import ToolWrapperObserver
from src.main.fr.tagc.wopmars.framework.rule.ToolWrapper import ToolWrapper
from src.main.fr.tagc.wopmars.utils.Logger import Logger

from src.main.fr.tagc.wopmars.utils.OptionManager import OptionManager
from src.main.fr.tagc.wopmars.utils.exceptions.WopMarsException import WopMarsException


class WorkflowManager(ToolWrapperObserver):
    """
    The WorkflowManager class manage all the software execution.

    He will ask the parser to build the DAG then execute it.
    """    
    def __init__(self):
        """
        Constructor of WorkflowManager.

        It initialize the parser with the path of the definition file given by the OptionManager.

        The parser will give the DAG which will be executed.
        The queue_exec is the Thread pool. It will contains the tools that will wait for being executed.
        The list_queue_buffer will be filled with the tool that the WorkflowManager couldn't execute.
        The count_exec is a counter that keep trace of the tools that are currently executed.
        The dag_tools will contian the dag representing the workflow.

        :return:
        """
        self.__parser = Parser(OptionManager()["DEFINITION_FILE"])
        self.__queue_exec = UniqueQueue()
        self.__list_queue_buffer = []
        self.__count_exec = 0
        self.__dag_tools = None

    def run(self):
        """
        Get the dag then execute it.

        The dag is taken thanks to the "parse()" method of the parser.
        Then, execute_from is called with no argument to get the origin nodes.
        :return:
        """
        self.__dag_tools = self.__parser.parse()
        self.execute_from()

    def execute_from(self, node=None):
        """
        Execute the dag from the given node.

        The next nodes are taken thanks to the "successors()" method of the DAG and are put into the queue.
        The "run_queue()" is then called.

        If node is set to None, the behavior of the function is the same.

        :param node: ToolWrapper a node of the DAG or None, if it executes from the root.
        :return: void
        """

        list_tw = self.__dag_tools.successors(node)
        Logger().debug("Next tools: " + str([t.__class__.__name__ for t in list_tw]))
        # The toolwrappers
        for tw in list_tw:
            self.__queue_exec.put(ToolThread(tw))

        self.run_queue()

    def run_queue(self):
        """
        Call start() method of all elements of the queue.

        The tools inside the queue are taken then their inputs are checked. If they are ready, the tools are started.
        If not, they are put in a buffer list of "not ready tools" of "ready but has not necessary ressources available
        tools".

        After that, the code check for the state of the workflow and gather the informations to see if the workflow
        are finished, if it encounter an error or if it is currently running.

        :raise WopMarsException: The workflow encounter a problem and must stop.
        :return: void
        """

        #
        # # TODO THIS METHOD IS NOT THREAD-SAFE
        #

        # If no tools have been added to the queue:
        #  - All tools have been executed and the queue is empty, so nothing happens
        #  - There were remaing tools in the queue but they weren't ready, so they are tested again
        while not self.__queue_exec.empty():
            Logger().debug("Queue size: " + str(self.__queue_exec.qsize()))
            thread_tw = self.__queue_exec.get()
            tw = thread_tw.get_toolwrapper()
            Logger().debug("Current ToolWrapper: " + str(tw.__class__.__name__))
            if tw.are_inputs_ready():
                Logger().debug("ToolWrapper ready: " + str(tw.__class__.__name__))
                # todo verification des ressources
                thread_tw.subscribe(self)
                self.__count_exec += 1
                # todo multithreading
                thread_tw.run()
            else:
                Logger().debug("ToolWrapper not ready: " + str(tw.__class__.__name__))
                # The buffer contains the ToolWrappers that have inputs which are not ready yet.
                self.__list_queue_buffer.append(thread_tw)

        Logger().debug("Buffer: " + str([t.get_toolwrapper().__class__.__name__ for t in self.__list_queue_buffer]))
        Logger().debug("Running ToolWrappers: " + str(self.__count_exec))

        # There is no more ToolWrapper that are waiting to be executed.
        # Is there some tools that are currently being executed?
        if self.__count_exec == 0:
            # Is there some tools that weren't ready?
            if len(self.__list_queue_buffer) == 0:
                # If there is no tool waiting and no tool being executed, the workflow has finished.
                Logger().info("The workflow has completed.")
                sys.exit()
            elif not self.check_buffer():
                # If there is no tool being executed but there is that are waiting something, the workflow has an issue
                raise WopMarsException("The workflow has failed.",
                                       "The inputs are not ready for the remaining tools: " +
                                       ", ".join([t.get_toolwrapper().__class__.__name__ for t in self.__list_queue_buffer]) + ". ")
            # If there is one tool that is ready, it means that it is in queue because ressources weren't available.

    def check_buffer(self):
        """
        Check if the buffer contains ToolWrapper that are ready.

        :return: bool: True if there is at least one toolwrapper that is READY in the buffer.
        """
        for tw in self.__list_queue_buffer:
            if tw.get_toolwrapper().get_state() == ToolWrapper.READY:
                return True
        return False

    def notify_success(self, thread_toolwrapper):
        """
        Handle toolwrapper success by continuing the dag.

        Implementation of the super class method.
        :param toolwrapper: ToolWrapper that just succeed
        :return:
        """
        Logger().info(str(thread_toolwrapper.get_toolwrapper().__class__.__name__) + " has succeed.")
        # Continue the dag execution from the toolwrapper that just finished.
        self.__count_exec -= 1
        self.execute_from(thread_toolwrapper.get_toolwrapper())

    def notify_failure(self, thread_toolwrapper):
        """
        Handle toolwrapper failure by re-puting it in the queue.

        :param toolwrapper: ToolWrapper that just failed
        :return:
        """
        pass

if __name__ == "__main__":
    OptionManager()["DEFINITION_FILE"] = "/home/giffon/Documents/wopmars/src/resources/example_def_file5.yml"
    OptionManager()["-v"] = 4
    OptionManager()["--dot"] = None
    my_workflow = WorkflowManager()
    my_workflow.run()
