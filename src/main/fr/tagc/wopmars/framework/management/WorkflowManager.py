"""
Module containing the WorkflowManager class
"""
import datetime
import sys

import time
from sqlalchemy import and_
from sqlalchemy.sql.functions import func

from src.main.fr.tagc.wopmars.framework.bdd.SQLManager import SQLManager
from src.main.fr.tagc.wopmars.framework.bdd.tables.Execution import Execution
from src.main.fr.tagc.wopmars.framework.bdd.tables.IODbPut import IODbPut
from src.main.fr.tagc.wopmars.framework.bdd.tables.IOFilePut import IOFilePut
from src.main.fr.tagc.wopmars.framework.bdd.tables.ToolWrapper import ToolWrapper
from src.main.fr.tagc.wopmars.framework.bdd.tables.Type import Type
from src.main.fr.tagc.wopmars.framework.management.DAG import DAG
from src.main.fr.tagc.wopmars.framework.management.ToolThread import ToolThread
from src.main.fr.tagc.wopmars.framework.management.ToolWrapperObserver import ToolWrapperObserver
from src.main.fr.tagc.wopmars.framework.parsing.Parser import Parser
from src.main.fr.tagc.wopmars.utils.PathFinder import PathFinder
from src.main.fr.tagc.wopmars.utils.Logger import Logger
from src.main.fr.tagc.wopmars.utils.OptionManager import OptionManager
from src.main.fr.tagc.wopmars.utils.UniqueQueue import UniqueQueue
from src.main.fr.tagc.wopmars.utils.exceptions.WopMarsException import WopMarsException


class WorkflowManager(ToolWrapperObserver):
    """
    The WorkflowManager class manage all the workflow execution.

    WorkflowManager will ask the parser to build the DAG then execute it. The execution of the DAG is done as following:
      1- The workflow manager take the "tool_dag" with all the rules of the workflow and build the "dag_to_exec" which
      will be actually executed.
      2- The method "execute_from()" is call without argument, meaning that the execution begin at the top of the dag
      (the root of the tree)
      3- The nodes are gathered thanks to the "successors" method of the DAG
      4- Each node is wrapped inside a ToolThread object which will be added to the queue
      5- Each ToolThread is executed (ordered) as follows:
        a- If the inputs are ready: they are executed
        b- If not, they are put in the buffer
      6- When the ToolThread has finished its execution, a notification of success is sent
      7- The method "execute_from" is called again with the succeeded ToolWrapper in arguments
      8- Loop to the 3rd step
      9- When the DAG is finished, the software exits

    Every exception or error are raised to the top level of the software (wopmars.py) through WopMarsException with
    a String explaining the context and details about the exception.
    """    
    def __init__(self):
        """
        Constructor of WorkflowManager.

        It initialize the parser with the path of the definition file given by the OptionManager.

        The parser will give the DAG which will be executed. The parser is instantiated with the "--wopfile"
        option given by the user.
        The queue_exec is the Thread pool. It will contains the tool threads that will wait for being executed.
        The list_queue_buffer will be filled with the tool threads that the WorkflowManager couldn't execute.
        The count_exec is a counter that keep trace of the tools that are currently executed.
        The dag_tools will contain the dag representing the workflow.
        The dag_to_exec is basically the same dag than dag_tools or a subgraph depending on the options --sourcerule or --targetrule
        given by the user.
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

        The database is setUp here if workflow tables have not been created yet.

        The dag is taken thanks to the "parse()" method of the parser.
        Then, execute_from is called with no argument to get the origin nodes.
        :return:
        """
        SQLManager.instance().create_all()
        self.__session.get_or_create(Type, defaults={"id": 1}, name="input")
        self.__session.get_or_create(Type, defaults={"id": 2}, name="output")
        self.__session.commit()
        self.__dag_tools = self.__parser.parse()
        self.get_dag_to_exec()
        self.execute_from()

    def erase_output(self, tw):
        list_outputs_path = [f.path for f in tw.files if f.type.name == "output"]
        Logger.instance().info("Forced execution implies overwrite existing output. Erasing files and tables.")
        s = ""
        for f_path in list_outputs_path:
            s += "\n" + f_path
            PathFinder.silentremove(f_path)
        Logger.instance().debug("Removed files:" + s)

        list_output_tables = [t.name.split(".")[-1] for t in tw.tables if t.type.name == "output"]
        s = ""
        for t_name in list_output_tables:
            s += "\n" + t_name
            SQLManager.instance().drop(t_name)
            SQLManager.instance().create(t_name)
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
        :return:
        """
        if OptionManager.instance()["--sourcerule"] is not None:
            try:
                node_from_rule = [n for n in self.__dag_tools if n.name == OptionManager.instance()["--sourcerule"]][0]
            except IndexError:
                raise WopMarsException(
                    "The given rule to start from: " + OptionManager.instance()["--sourcerule"] + " doesn't exist.")

            self.__dag_to_exec = DAG(self.__dag_tools.get_all_successors(node_from_rule))
            Logger.instance().info("Running the workflow from rule " + str(OptionManager.instance()["--sourcerule"]) +
                                   " -> " + node_from_rule.toolwrapper)
        elif OptionManager.instance()["--targetrule"] is not None:
            try:
                node_from_rule = [n for n in self.__dag_tools if n.name == OptionManager.instance()["--targetrule"]][0]
            except IndexError:
                raise WopMarsException(
                    "The given rule to go to: " + OptionManager.instance()["--targetrule"] + " doesn't exist.")
            self.__dag_to_exec = DAG(self.__dag_tools.get_all_predecessors(node_from_rule))
            Logger.instance().info("Running the workflow to the rule " + str(OptionManager.instance()["--targetrule"]) +
                                   " -> " + node_from_rule.toolwrapper)
        else:
            self.__dag_to_exec = self.__dag_tools

        for tw in set(self.__dag_tools.nodes()).difference(set(self.__dag_to_exec.nodes()   )):
            tw.set_execution_infos(status="NOT_PLANNED")
            self.__session.add(tw)
        self.__session.commit()

    def execute_from(self, tw=None):
        """
        Execute the dag from the toolwrappers in the list given.

        The next nodes are taken thanks to the "successors()" method of the DAG and are put into the queue.
        The "run_queue()" is then called.

        A trace of the already_runned ToolWrapper objects is kept in order to avoid duplicate execution.

        :param node: ToolWrapper a node of the DAG or None, if it executes from the root.
        :return: void
        """
        list_tw = self.__dag_to_exec.successors(tw)
        Logger.instance().debug("Next tools: " + str([t.__class__.__name__ for t in list_tw]))

        for tw in list_tw:
            #      T1
            #    /   \
            #   |    T2
            #    \   /
            #      T3
            # In the case above, the T3 could be executed twice if the output of T2 is already available at the begining
            # (re-execution without clean)
            if tw not in self.__already_runned:
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
        If not, they are put in a buffer list of "not ready tools" of "ready but has not necessary ressources available
        tools".

        The start method is called with a dry argument, if it appears that the input of the ToolWrapper are the same
        than in a previous execution, and that the output are already ready. The dry parameter is set to True and the
        start method will only simulate the execution.

        After that, the code check for the state of the workflow and gather the informations to see if the workflow
        are finished, if it encounter an error or if it is currently running.

        :raise WopMarsException: The workflow encounter a problem and must stop.
        :return: void
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
            thread_tw = self.__queue_exec.get()
            tw = thread_tw.get_toolwrapper()
            Logger.instance().debug("Current rule: " + tw.name + "->" + tw.toolwrapper)
            if not self.all_predecessors_have_run(tw):
                Logger.instance().debug("Predecessors of rule: " + tw.name + " have not been executed yet.")
            elif tw.are_inputs_ready() or OptionManager.instance()["--dry-run"]:
                tw.set_args_date_and_size("input")
                Logger.instance().debug("ToolWrapper ready: " + tw.toolwrapper)
                dry = False
                if not OptionManager.instance()["--forceall"] and \
                        self.is_this_tool_already_done(tw):
                    Logger.instance().info("Rule: " + tw.name + " -> " + tw.toolwrapper +
                                           " seemed to have already" +
                                           " been runned with same" +
                                           " parameters.")
                    dry = True
                elif OptionManager.instance()["--forceall"] and not OptionManager.instance()["--dry-run"]:
                    self.erase_output(tw)
                # todo twthread verification des ressources
                thread_tw.subscribe(self)
                self.__count_exec += 1
                # todo twthread methode start
                thread_tw.set_dry(dry)
                try:
                    thread_tw.run()
                except Exception as e:
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
                sys.exit(0)
            # uniquement en environnement multiThreadpredece
            elif not self.check_buffer():
                # If there is no tool being executed but there is that are waiting something, the workflow has an issue
                raise WopMarsException("The workflow has failed.",
                                       "The inputs are not ready for the remaining tools: " +
                                       ", \n".join([t.get_toolwrapper().toolwrapper +
                                                  " -> rule: " +
                                                  t.get_toolwrapper().name for t in self.__list_queue_buffer]) + ". ")
            # If there is one tool that is ready, it means that it is in queue because ressources weren't available.

    def set_finishing_informations(self, finished_at, status):
        modify_exec = self.__session.query(Execution).order_by(Execution.id.desc()).first()
        modify_exec.finished_at = finished_at
        modify_exec.time = (modify_exec.finished_at - modify_exec.started_at).total_seconds()
        modify_exec.status = status
        self.__session.add(modify_exec)
        self.__session.commit()

    def all_predecessors_have_run(self, tw):
        return self.__dag_to_exec.get_all_predecessors(tw).difference(set([tw])).issubset(set(self.__already_runned))

    @staticmethod
    def is_this_tool_already_done(tw):
        """
        Return True if conditions for saying "The output of this ToolWrapper are already available" are filled.

        The conditions are:
            - The ToolWrapper exist in bdd (named = tw_old)
            - The tw_old param are the same than the same which is about to start
            - the tw_old inputs are the same
            - the tw_old outputs are ok and ready

        :param tw:
        :return:
        """
        session = SQLManager.instance().get_session()
        list_same_toolwrappers = session.query(ToolWrapper).filter(ToolWrapper.toolwrapper == tw.toolwrapper)\
            .filter(ToolWrapper.execution_id != tw.execution_id).all()
        i = 0
        while i < len(list_same_toolwrappers):
            if list_same_toolwrappers[i] != tw or \
                    not list_same_toolwrappers[i].same_input_than(tw) or \
                    not list_same_toolwrappers[i].is_output_ok():
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
        :return:
        """
        self.__session.add(thread_toolwrapper.get_toolwrapper())
        self.__session.commit()

        dry_status = thread_toolwrapper.get_dry()
        if not OptionManager.instance()["--dry-run"]:
            thread_toolwrapper.get_toolwrapper().set_args_date_and_size("output", dry_status)
        if dry_status == False and not OptionManager.instance()["--dry-run"]:
            Logger.instance().info(str(thread_toolwrapper.get_toolwrapper().__class__.__name__) + " has succeed.")
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
