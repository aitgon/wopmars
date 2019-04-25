import datetime
import sys

import time

from wopmars.framework.database.SQLManager import SQLManager
from wopmars.framework.database.tables.Execution import Execution
from wopmars.framework.database.tables.IODbPut import IODbPut
from wopmars.framework.database.tables.ToolWrapper import ToolWrapper
from wopmars.framework.database.tables.Type import Type
from wopmars.framework.management.DAG import DAG
from wopmars.framework.management.ToolThread import ToolThread
from wopmars.framework.management.ToolWrapperObserver import ToolWrapperObserver
from wopmars.framework.parsing.Parser import Parser
from wopmars.utils.PathFinder import PathFinder
from wopmars.utils.Logger import Logger
from wopmars.utils.OptionManager import OptionManager
from wopmars.utils.UniqueQueue import UniqueQueue
from wopmars.utils.exceptions.WopMarsException import WopMarsException


class WorkflowManager(ToolWrapperObserver):
    """
    The WorkflowManager class manage all the workflow execution.

    WorkflowManager will ask the parser to build the DAG then execute it. The execution of the DAG is done as following:

    1- The workflow manager take the "tool_dag" with all the rules of the workflow and build the "dag_to_exec" which
    will be actually executed according to the "target rule" and "source rule" options.
    2- The method :meth:`~.wopmars.framework.management.WorkflowManager.WorkflowManager.execute_from` is call without argument, meaning that the execution begin at the top of the dag
    (the root of the tree).
    3- The nodes are gathered thanks to the :meth:`~.wopmars.framework.management.DAG.DAG.successors` method of the :class:`wopmars.framework.management.DAG.DAG`
    4- Each node is wrapped inside a :class:`~.wopmars.framework.management.ToolThread.ToolThread` object which will be added to the queue.
    5- Each ToolThread is executed (ordered) as follows:

      a- If the inputs are ready: they are executed.
      b- If not, they are put in the buffer.

    6- When the :class:`~.wopmars.framework.management.ToolThread.ToolThread` has finished its execution, a notification of success is sent.
    7- The method :meth:`~wopmars.framework.management.WorkflowManager.WorkflowManager.execute_from` is called again with the succeeded ToolWrapper as argument.
    8- Loop to the 3rd step
    9- When the DAG is finished, the software exits

    Every exception or error are raised to the top level of the software through WopMarsException with
    a String explaining the context and details about the exception.
    """    
    def __init__(self):
        """
        The parser will give the DAG which will be executed.
        The queue_exec is the Thread pool. It will contains the tool threads that will wait for being executed. Each tool
        should appear only once in the queue.
        The list_queue_buffer will be filled with the tool threads that the WorkflowManager couldn't execute.
        The count_exec is a counter that keep trace of the number of tools that are currently executed.
        The dag_tools will contain the dag representing the workflow.
        The dag_to_exec is basically the same dag than dag_tools or a subgraph depending on the options --sourcerule or --targetrule
        given by the user.
        The session is used to get back the session without calling again SQLManager.
        """
        self.__parser = Parser()
        self.__queue_exec = UniqueQueue()
        self.__list_queue_buffer = []
        self.__count_exec = 0
        self.__dag_tools = None
        self.__dag_to_exec = None
        self.__already_runned = set()
        self.__session = SQLManager.instance().get_session()

    def run(self):
        """
        Get the dag then execute it.

        The database is setUp here if workflow side tables have not been created yet.

        The dag is taken thanks to the :meth:`~.wopmars.framework.parsing.Parser.Parser.parse` method of the parser. And then pruned by the :meth:`~.wopmars.framework.management.WorkflowManager.WorkflowManager.get_dag_to_exec` method
        which will set the right DAG to be executed.
        Then, :meth:`~.wopmars.framework.management.WorkflowManager.WorkflowManager.execute_from` is called with no argument to get the origin nodes.
        """

        # This create_all is supposed to only create workflow-management side tables (called "wom_*")
        SQLManager.instance().create_all()

        if OptionManager.instance()["--clear-history"]:
            Logger.instance().info("Deleting WoPMaRS history...")
            SQLManager.instance().drop_table_content_list(SQLManager.wom_table_names)

        # The following lines allow to create types 'input' and 'output' in the db if they don't exist.
        self.__session.get_or_create(Type, defaults={"id": 1}, name="input")
        self.__session.get_or_create(Type, defaults={"id": 2}, name="output")
        self.__session.commit()
        # Get the DAG representing the whole workflow
        self.__dag_tools = self.__parser.parse()
        # Build the DAG which is willing to be executed according
        self.get_dag_to_exec()
        # Start the execution at the root nodes
        if OptionManager.instance()["--forceall"] and not OptionManager.instance()["--dry-run"]:
            self.erase_output()
        self.execute_from()

    def erase_output(self):
        """
        Erase the outputs of the DAG that will be executed in order to prevents conflicts.
        """
        list_tw = self.__dag_to_exec.nodes()
        set_files = set()
        set_tables = set()

        Logger.instance().info("Forced execution implies overwrite existing output. Erasing files and tables.")
        for tw in list_tw:
           [set_files.add(f.path) for f in tw.files if f.type.name == "output"]
           [set_tables.add(t.tablename) for t in tw.tables if t.type.name == "output"]

        s = ""
        for f_path in set_files:
            s += "\n" + f_path
            PathFinder.silentremove(f_path)
        Logger.instance().debug("Removed files:" + s)

        SQLManager.instance().drop_table_content_list(
            set(IODbPut.tablenames).intersection(set_tables))

        s = "\n"
        s += "\n".join(set_tables)
        Logger.instance().debug("Removed tables content:" + s)

        Logger.instance().info("Output files and tables from previous execution have been erased.")

    def get_dag_to_exec(self):
        """
        Set the dag to exec in terms of --sourcerule option and --targetrule option.

        The source rule is checked first (there should not be both set because of the checks at the begining of the software)

        If sourcerule is set, then it is its successors that are searched in the whole dag.
        Else, it is its predecessors.

        The set of obtained rules are used to build the "dag_to_exec". The nodes returned by get_all_successors and
        get_all_predecessors are implicitly all related.
        """
        if OptionManager.instance()["--sourcerule"] is not None:
            try:
                # Get the rule asked by the user as 'sourcerule'
                node_from_rule = [n for n in self.__dag_tools if n.name == OptionManager.instance()["--sourcerule"]][0]
            except IndexError:
                raise WopMarsException(
                    "The given rule to start from: " + OptionManager.instance()["--sourcerule"] + " doesn't exist.")

            self.__dag_to_exec = DAG(self.__dag_tools.get_all_successors(node_from_rule))
            Logger.instance().info("Running the workflow from rule " + str(OptionManager.instance()["--sourcerule"]) +
                                   " -> " + node_from_rule.toolwrapper)
        elif OptionManager.instance()["--targetrule"] is not None:
            try:
                # Get the rule asked by the user as 'targetrule'
                node_from_rule = [n for n in self.__dag_tools if n.name == OptionManager.instance()["--targetrule"]][0]
            except IndexError:
                raise WopMarsException(
                    "The given rule to go to: " + OptionManager.instance()["--targetrule"] + " doesn't exist.")
            self.__dag_to_exec = DAG(self.__dag_tools.get_all_predecessors(node_from_rule))
            Logger.instance().info("Running the workflow to the rule " + str(OptionManager.instance()["--targetrule"]) +
                                   " -> " + node_from_rule.toolwrapper)
        else:
            self.__dag_to_exec = self.__dag_tools

        # ???
        # todo checkout what is going on here
        tables = []
        [tables.extend(tw.tables) for tw in self.__dag_to_exec.nodes()]
        IODbPut.set_tables_properties(tables)

        # For the tools that are in the workflow definition file but not in the executed dag, their status is set to
        # "NOT_PLANNED"
        for tw in set(self.__dag_tools.nodes()).difference(set(self.__dag_to_exec.nodes())):
            tw.set_execution_infos(status="NOT_PLANNED")
            self.__session.add(tw)

        self.__session.commit()

    def execute_from(self, tw=None):
        """
        Execute the dag from the toolwrappers in the list given.

        The next nodes are taken thanks to the "successors()" method of the DAG and are put into the queue.
        The "run_queue()" is then called.

        A trace of the already_runned ToolWrapper objects is kept in order to avoid duplicate execution.

        :param node: A node of the DAG or None, if it needs to be executed from the root.
        :type node: :class:`~.wopmars.framework.database.tables.ToolWrapper.ToolWrapper`
        :return: void
        """
        # the first list will be the root nodes
        list_tw = self.__dag_to_exec.successors(tw)
        Logger.instance().debug("Next tools: " + str([t.__class__.__name__ for t in list_tw]))

        for tw in list_tw:
            # every rule should be executed once and only once
            if tw not in self.__already_runned:
                # ToolThread object is a thread ready to start
                self.__queue_exec.put(ToolThread(tw))
            else:
                Logger.instance().debug("Rule: " + tw.name +
                                        " -> " + tw.toolwrapper +
                                        " has already been executed. Pass.")
        self.run_queue()

    def run_queue(self):
        """
        Call start() method of all elements of the queue.

        The tools inside the queue are taken then their inputs are checked. If they are ready, the tools are started.
        If not, they are put in a buffer list of "not ready tools" or "ready but has not necessary ressources available
        tools".

        The start method is called with a dry argument, if it appears that the input of the ToolWrapper are the same
        than in a previous execution, and that the output are already ready. The dry parameter is set to True and the
        start method will only simulate the execution.

        After that, the code check for the state of the workflow and gather the informations to see if the workflow
        is finished, if it encounter an error or if it is currently running.

        :raises WopMarsException: The workflow encounter a problem and must stop.
        """

        #
        # # TODO THIS METHOD IS NOT THREAD-SAFE (peut etre que si, à voir)
        #

        # If no tools have been added to the queue:
        #  - All tools have been executed and the queue is empty, so nothing happens
        #  - There were remaing tools in the queue but they weren't ready, so they are tested again
        while not self.__queue_exec.empty():
            Logger.instance().debug("Queue size: " + str(self.__queue_exec.qsize()))
            Logger.instance().debug("Queue content: " + str(["rule: " + tt.get_toolwrapper().name + "->" +
                                                             tt.get_toolwrapper().toolwrapper for tt in self.__queue_exec.get_queue_tuple()]))
            # get the first element of the queue to execute
            thread_tw = self.__queue_exec.get()
            tw = thread_tw.get_toolwrapper()
            Logger.instance().debug("Current rule: " + tw.name + "->" + tw.toolwrapper)
            # check if the predecessors of a rule have been already executed: a rule shouldn't be executed if
            # its predecessors have not been executed yet
            if not self.all_predecessors_have_run(tw):
                Logger.instance().debug("Predecessors of rule: " + tw.name + " have not been executed yet.")
            # for running, either the inputs have to be ready or the dry-run mode is enabled
            elif tw.are_inputs_ready() or OptionManager.instance()["--dry-run"]:
                # the state of inputs (table and file) are set in the db here.
                tw.set_args_date_and_size("input")
                Logger.instance().debug("ToolWrapper ready: " + tw.toolwrapper)
                dry = False
                # if forceall option, then the tool is reexecuted anyway
                # check if the actual execution of the toolwrapper is necessary
                # every predecessors of the toolwrapper have to be executed (or simulated)
                if not OptionManager.instance()["--forceall"] and \
                        self.is_this_tool_already_done(tw) and \
                        not bool([node for node in self.__dag_to_exec.predecessors(tw) if node.status != "EXECUTED" and
                                        node.status != "ALREADY_EXECUTED"]):
                    Logger.instance().info("Rule: " + tw.name + " -> " + tw.toolwrapper +
                                           " seemed to have already" +
                                           " been runned with same" +
                                           " parameters.")
                    dry = True

                # todo twthread verification des ressources
                thread_tw.subscribe(self)
                self.__count_exec += 1
                # todo twthread methode start
                thread_tw.set_dry(dry)
                try:
                    # be carefull here: the execution of the toolthreads is recursive meaning that calls to function may
                    # be stacked (run -> notify success -> run(next tool) -> notify success(next tool) -> etc....
                    # todo twthread methode start
                    thread_tw.run()
                except Exception as e:
                    # as mentionned above, there may be recursive calls to this function, so every exception can
                    # pass here multiple times: this attribute is used for recognizing exception that have already been
                    # caught
                    if not hasattr(e, "teb_already_seen"):
                        setattr(e, "teb_already_seen", True)
                        tw.set_execution_infos(status="EXECUTION_ERROR")
                        self.__session.add(tw)
                        self.__session.commit()
                    raise e
            else:
                Logger.instance().debug("ToolWrapper not ready: rule: " + tw.name + " -> " + str(tw.toolwrapper))
                # The buffer contains the ToolWrappers that have inputs which are not ready yet.
                self.__list_queue_buffer.append(thread_tw)

        Logger.instance().debug("Buffer: " + str(["rule: " + t.get_toolwrapper().name + "->" +
                                                  t.get_toolwrapper().toolwrapper for t in self.__list_queue_buffer]))
        Logger.instance().debug("Running rules: " + str(self.__count_exec))

        # There is no more ToolWrapper that are waiting to be executed.
        # Is there some tools that are currently being executed?
        if self.__count_exec == 0:
            # Is there some tools that weren't ready?
            if len(self.__list_queue_buffer) == 0:
                # If there is no tool waiting and no tool being executed, the workflow has finished.
                finished_at = datetime.datetime.fromtimestamp(time.time())
                Logger.instance().info("The workflow has completed. Finished at: " + str(finished_at))
                self.set_finishing_informations(finished_at, "FINISHED")
                SQLManager.instance().get_session().close()
                sys.exit(0)
            # uniquement en environnement multiThreadpredece
            elif not self.check_buffer():
                # If there is no tool being executed but there is that are waiting something, the workflow has an issue
                finished_at = datetime.datetime.fromtimestamp(time.time())
                tw_list = [t.get_toolwrapper() for t in self.__list_queue_buffer]
                if len(tw_list) > 0:
                    input_files_not_ready = tw_list[0].get_input_files_not_ready()
                    self.set_finishing_informations(finished_at, "ERROR")
                    raise WopMarsException("The workflow has failed.",
                                           "The inputs '{}' have failed for this tool '{}'".format(input_files_not_ready[0], tw_list[0].name))
                                           # "The inputs are not ready for thisto: " +
                                           # ", \n".join([t.get_toolwrapper().toolwrapper +
                                           #            " -> rule: " +
                                           #            t.get_toolwrapper().name for t in self.__list_queue_buffer]) + ". ")
            # If there is one tool that is ready, it means that it is in queue because ressources weren't available.

    def set_finishing_informations(self, finished_at, status):
        """
        Set the finsihing information of the whole workflow.

        :param finished_at: The finishing date of the workflow
        :type finished_at: datetime.datetime
        :param status: The final status of the workflow
        :type status: str
        """
        modify_exec = self.__session.query(Execution).order_by(Execution.id.desc()).first()
        if modify_exec is not None:
            modify_exec.finished_at = finished_at
            modify_exec.time = (modify_exec.finished_at - modify_exec.started_at).total_seconds()
            modify_exec.status = status
            self.__session.add(modify_exec)
            self.__session.commit()

    def all_predecessors_have_run(self, tw):
        """
        Check if all the predecessors of the given toolwrapper have yet been executed in this workflow.

        :param tw: Node of the DAG
        :type tw: :class:`~.wopmars.main.framework.database.tables.ToolWrapper.ToolWrapper`
        :return: Bool
        """
        return bool(self.__dag_to_exec.get_all_predecessors(tw).difference(set([tw])).issubset(set(self.__already_runned)))

    @staticmethod
    def is_this_tool_already_done(tw):
        """
        Return True if conditions for saying "The output of this ToolWrapper are already available" are filled.

        The conditions are:
            - The ToolWrapper exist in database (named = tw_old)
            - The tw_old param are the same than the same which is about to start
            - the tw_old inputs are the same
            - the tw_old outputs exists with the same name and are more recent than inputs

        :param tw: The Toolwrapper to test_bak
        :type tw: :class:`~.wopmars.main.framework.database.tables.ToolWrapper.ToolWrapper`
        """
        session = SQLManager.instance().get_session()
        list_same_toolwrappers = session.query(ToolWrapper).filter(ToolWrapper.toolwrapper == tw.toolwrapper)\
            .filter(ToolWrapper.execution_id != tw.execution_id).all()
        i = 0
        while i < len(list_same_toolwrappers):
            same = False
            # two tw are equals if they have the same parameters, the same file names and path
            # and the same table names and models
            if list_same_toolwrappers[i] == tw and \
                    list_same_toolwrappers[i].does_output_exist() and \
                    list_same_toolwrappers[i].is_output_more_recent_than_input():
                    same = True
            if not same:
                del list_same_toolwrappers[i]
            else:
                i += 1

        # The elements of the list have been removed if none fit the conditions
        return bool(list_same_toolwrappers)

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
        Handle thread_toolwrapper success by continuing the dag.

        :param thread_toolwrapper: ToolWrapper thread that just succeed
        :type thread_toolwrapper: :class:`~.wopmars.management.ToolThread.ToolThread`
        """
        self.__session.add(thread_toolwrapper.get_toolwrapper())
        self.__session.commit()

        dry_status = thread_toolwrapper.get_dry()
        # if not OptionManager.instance()["--dry-run"]:
        #     thread_toolwrapper.get_toolwrapper().set_args_date_and_size("output", dry_status)
        if dry_status is False and not OptionManager.instance()["--dry-run"]:
            Logger.instance().info("Rule " + str(thread_toolwrapper.get_toolwrapper().name) + " -> " + str(thread_toolwrapper.get_toolwrapper().__class__.__name__) + " has succeed.")
        # Continue the dag execution from the toolwrapper that just finished.
        self.__already_runned.add(thread_toolwrapper.get_toolwrapper())
        self.__count_exec -= 1

        if len(self.__list_queue_buffer):
            Logger.instance().debug("Fill the queue with the Buffer: " +
                                    str([t.get_toolwrapper().__class__.__name__ for t in self.__list_queue_buffer]))
        i = 0
        for tw_thread in self.__list_queue_buffer:
            self.__queue_exec.put(tw_thread)
            del self.__list_queue_buffer[i]
            i += 1

        self.execute_from(thread_toolwrapper.get_toolwrapper())

    def notify_failure(self, thread_toolwrapper):
        """
        Handle thread_toolwrapper failure by re-puting it in the queue.

        :param thread_toolwrapper: ToolWrapper thread that just failed
        :return:
        """
        pass
