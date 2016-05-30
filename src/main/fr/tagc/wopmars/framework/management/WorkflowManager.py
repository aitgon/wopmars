"""
Module containing the WorkflowManager class
"""
from queue import Queue


from fr.tagc.wopmars.framework.parsing.Parser import Parser
from fr.tagc.wopmars.framework.management.ToolWrapperObserver import ToolWrapperObserver


# todo test sur cette classe
class WorkflowManager(ToolWrapperObserver):
    """
    The WorkflowManager class manage all the software execution.

    He will ask the parser to build the DAG then execute it.
    """    
    def __init__(self, path):
        """
        First line short documentation
        
        More documentation
        :param something:
        :return:
        """
        # Todo optionmanager
        self.__parser = Parser(path)
        self.__queue_exec = Queue()
        self.__dag_tools = None

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
        while not self.__queue_exec.empty():
            tw = self.__queue_exec.get()
            tw.subscribe(self)
            tw.start()

    def notify_success(self, toolwrapper):
        """
        Handle toolwrapper success by continuing the dag.

        Implementation of the super class method.
        :param toolwrapper: ToolWrapper that just succeed
        :return:
        """
        # todo loging
        print(str(toolwrapper.__class__.__name__) + " a fini.")
        # Continue the dag execution from the toolwrapper that just finished.
        self.execute_from(toolwrapper)

    def notify_failure(self, toolwrapper):
        """
        Handle toolwrapper failure by re-puting it in the queue.

        :param toolwrapper: ToolWrapper that just failed
        :return:
        """
        # todo loging
        print(str(toolwrapper.__class__.__name__) + " a échoué.")
        self.__queue_exec.put(toolwrapper)

if __name__ == "__main__":
    my_workflow = WorkflowManager("/home/giffon/Documents/wopmars/src/resources/example_def_file3.yml")
    my_workflow.run()
