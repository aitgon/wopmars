import sys

from wopmars.SQLManager import SQLManager
from wopmars.models.Execution import Execution
from wopmars.models.TableInputOutputInformation import TableInputOutputInformation
from wopmars.models.ToolWrapper import ToolWrapper
from wopmars.models.TypeInputOrOutput import TypeInputOrOutput
from wopmars.DAG import DAG
from wopmars.ToolWrapperThread import ToolWrapperThread
from wopmars.ToolWrapperObserver import ToolWrapperObserver
from wopmars.Parser import Parser
from wopmars.utils.Logger import Logger
from wopmars.utils.OptionManager import OptionManager
from wopmars.utils.UniqueQueue import UniqueQueue
from wopmars.utils.WopMarsException import WopMarsException
from wopmars.utils.various import get_current_time


class WorkflowManager(ToolWrapperObserver):
    """
    The WorkflowManager class manage all the workflow execution.

    WorkflowManager will ask the parser to build the DAG then execute it. The execution of the DAG is done as following:

    1- The workflow manager take the "tool_dag" with all the rules of the workflow and build the "dag_to_exec" which
    will be actually executed according to the "target rule" and "source rule" options.
    2- The method :meth:`~.wopmars.framework.management.WorkflowManager.WorkflowManager.execute_from` is call without argument, meaning that the execution begin at the top of the dag
    (the root of the tree).
    3- The nodes are gathered thanks to the :meth:`~.wopmars.framework.management.DAG.DAG.successors` method of the :class:`wopmars.framework.management.DAG.DAG`
    4- Each node is wrapped inside a :class:`~.wopmars.framework.management.ToolWrapperThread.ToolWrapperThread` object which will be added to the queue.
    5- Each ToolWrapperThread is executed (ordered) as follows:

      a- If the inputs are ready: they are executed.
      b- If not, they are put in the buffer.

    6- When the :class:`~.wopmars.framework.management.ToolWrapperThread.ToolWrapperThread` has finished its execution, a notification of success is sent.
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
        The dag_to_exec is basically the same dag than dag_tools or a subgraph depending on the options --since or --until
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

        The database is setUp here if workflow side models have not been created yet.

        The dag is taken thanks to the :meth:`~.wopmars.framework.parsing.Parser.Parser.parse` method of the parser. And then pruned by the :meth:`~.wopmars.framework.management.WorkflowManager.WorkflowManager.get_dag_to_exec` method
        which will set the right DAG to be executed.
        Then, :meth:`~.wopmars.framework.management.WorkflowManager.WorkflowManager.execute_from` is called with no argument to get the origin nodes.
        """

        # This create_all is supposed to only create workflow-management side models (called "wom_*")
        SQLManager.instance().create_all()

        # if OptionManager.instance()["--cleanup-metadata"]:
        #     Logger.instance().info("Deleting WoPMaRS history...")
        #     SQLManager.instance().drop_table_content_list(SQLManager.wopmars_history_tables)

        # The following lines allow to create types 'input' and 'output' in the db if they don't exist.
        self.__session.get_or_create(TypeInputOrOutput, defaults={"is_input": True}, is_input=True)
        self.__session.get_or_create(TypeInputOrOutput, defaults={"is_input": False}, is_input=False)
        self.__session.commit()
        # Get the DAG representing the whole workflow
        self.__dag_tools = self.__parser.parse()
        # Build the DAG which is willing to be executed according
        self.get_dag_to_exec()
        # Aitor has removed this command that removed everything before forceall
        # if OptionManager.instance()["--forceall"] and not OptionManager.instance()["--dry-run"]:
        #     self.erase_output()
        # Start the execution at the root nodes
        self.execute_from()

    def get_dag_to_exec(self):
        """
        Set the dag to exec in terms of --since option and --until option.

        The source rule is checked first (there should not be both set because of the checks at the begining of the software)

        If sourcerule is set, then it is its successors that are searched in the whole dag.
        Else, it is its predecessors.

        The set of obtained rules are used to build the "dag_to_exec". The nodes returned by get_all_successors and
        get_all_predecessors are implicitly all related.
        """
        if OptionManager.instance()["--since"] is not None:
            try:
                # Get the rule asked by the user as 'sourcerule'
                node_from_rule = [n for n in self.__dag_tools if n.rule_name == OptionManager.instance()["--since"]][0]
            except IndexError:
                raise WopMarsException(
                    "The given rule to start from: " + OptionManager.instance()["--since"] + " doesn't exist.")

            self.__dag_to_exec = DAG(self.__dag_tools.get_all_successors(node_from_rule))
            Logger.instance().info("Running the workflow from rule " + str(OptionManager.instance()["--since"]) +
                                   " -> " + node_from_rule.tool_python_path)
        elif OptionManager.instance()["--until"] is not None:
            try:
                # Get the rule asked by the user as 'targetrule'
                node_from_rule = [n for n in self.__dag_tools if n.rule_name == OptionManager.instance()["--until"]][0]
            except IndexError:
                raise WopMarsException(
                    "The given rule to go to: " + OptionManager.instance()["--until"] + " doesn't exist.")
            self.__dag_to_exec = DAG(self.__dag_tools.get_all_predecessors(node_from_rule))
            Logger.instance().info("Running the workflow to the rule " + str(OptionManager.instance()["--until"]) +
                                   " -> " + node_from_rule.tool_python_path)
        else:
            self.__dag_to_exec = self.__dag_tools

        # ???
        # totodo LucG checkout what is going on here
        tables = []
        [tables.extend(tw.relation_toolwrapper_to_tableioinfo) for tw in self.__dag_to_exec.nodes()]
        TableInputOutputInformation.set_tables_properties(tables)

        # For the tools that are in the workflow definition file but not in the executed dag, their status is set to
        # "NOT_PLANNED"
        # Update AG: if not planned, it will not be stored
        for tool_wrapper in set(self.__dag_tools.nodes()).difference(set(self.__dag_to_exec.nodes())):
            # tw.set_execution_infos(status="NOT_PLANNED")
            # self.__session.add(tw)
            self.__session.delete(tool_wrapper)

        self.__session.commit()

    def execute_from(self, tw=None):
        """
        Execute the dag from the toolwrappers in the list given.

        The next nodes are taken thanks to the "successors()" method of the DAG and are put into the queue.
        The "run_queue()" is then called.

        A trace of the already_runned ToolWrapper objects is kept in order to avoid duplicate execution.

        :param node: A node of the DAG or None, if it needs to be executed from the root.
        :type node: :class:`~.wopmars.framework.database.models.ToolWrapper.ToolWrapper`
        :return: void
        """
        # the first list will be the root nodes
        list_tw = self.__dag_to_exec.successors(tw)
        Logger.instance().debug("Next tools: " + str([t.__class__.__name__ for t in list_tw]))

        for tw in list_tw:
            # every rule should be executed once and only once
            if tw not in self.__already_runned:
                # ToolWrapperThread object is a thread ready to start
                self.__queue_exec.put(ToolWrapperThread(tw))
            else:
                Logger.instance().debug("ToolWrapper: " + tw.rule_name +
                                        " -> " + tw.tool_python_path +
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
        # # toTODO LucG THIS METHOD IS NOT THREAD-SAFE (peut etre que si, à voir)
        #

        ################################################################################################################
        #
        # Main while
        # If no tools have been added to the queue:
        #  - All tools have been executed and the queue is empty, so nothing happens
        #  - There were remaining tools in the queue but they weren't ready, so they are tested again
        #
        ################################################################################################################

        while not self.__queue_exec.empty():
            Logger.instance().debug("Queue size: " + str(self.__queue_exec.qsize()))
            Logger.instance().debug("Queue content: " + str(["rule: " + tt.get_toolwrapper().rule_name + "->" +
                                                             tt.get_toolwrapper().tool_python_path for tt in self.__queue_exec.get_queue_tuple()]))

            ############################################################################################################
            #
            # get the first element of the queue to execute
            #
            ############################################################################################################

            tool_wrapper_thread = self.__queue_exec.get()
            tool_wrapper = tool_wrapper_thread.get_toolwrapper()

            Logger.instance().debug("Current rule: " + tool_wrapper.rule_name + "->" + tool_wrapper.tool_python_path)
            # check if the predecessors of a rule have been already executed: a rule shouldn't be executed if
            # its predecessors have not been executed yet
            if not self.all_predecessors_have_run(tool_wrapper):
               Logger.instance().debug("Predecessors of rule: " + tool_wrapper.rule_name + " have not been executed yet.")

            ############################################################################################################
            #
            # Ready for running, either inputs are ready or dry-run mode is enabled
            #
            ############################################################################################################

            elif tool_wrapper.are_inputs_ready() or OptionManager.instance()["--dry-run"]:
                # the state of inputs (table and file) are set in the db here.
                tool_wrapper.set_args_time_and_size(1)
                Logger.instance().debug("ToolWrapper ready: " + tool_wrapper.tool_python_path)
                dry = False

                ############################################################################################################
                #
                # Will set to dry (ie. will not execute) if all these conditions are true
                # - not in forceall mode
                # - tool already executed previously
                # - some predecessors of this tool wrapper has not been executed
                #
                ############################################################################################################

                # check if the actual execution of the tool_python_path is necessary
                # every predecessors of the tool_python_path have to be executed (or simulated)
                # will not execute and set to dry if all these options

                if not OptionManager.instance()["--forceall"] and not OptionManager.instance()["--touch"]:  # if not in forceall option
                    if self.is_this_tool_wrapper_already_executed(tool_wrapper):  # this tool wrapper already executed
                        # some predecessors of this tool wrapper has not been executed
                        if not bool([tool_wrapper_predecessor for tool_wrapper_predecessor
                                     in self.__dag_to_exec.predecessors(tool_wrapper)
                                     if tool_wrapper_predecessor.status != "EXECUTED"
                                        and tool_wrapper_predecessor.status != "ALREADY_EXECUTED"]):
                            Logger.instance().info("ToolWrapper: {} -> {} seems to have already been run with same parameters."
                                                   .format(tool_wrapper.rule_name, tool_wrapper.tool_python_path))
                            dry = True

                # totodo lucg twthread verification des resources
                tool_wrapper_thread.subscribe(self)
                self.__count_exec += 1
                # totodo lucg twthread methode start
                tool_wrapper_thread.set_dry(dry)
                try:
                    # be careful here: the execution of the toolthreads is recursive meaning that calls to function may
                    # be stacked (run -> notify success -> run(next tool) -> notify success(next tool) -> etc....
                    # totodo lucg twthread methode start
                    tool_wrapper_thread.run()
                except Exception as e:
                    # as mentioned above, there may be recursive calls to this function, so every exception can
                    # pass here multiple times: this attribute is used for recognizing exception that have already been
                    # caught
                    if not hasattr(e, "teb_already_seen"):
                        setattr(e, "teb_already_seen", True)
                        tool_wrapper.set_execution_infos(status="ERROR")
                        self.__session.add(tool_wrapper)
                        self.__session.commit()
                    raise e
            else:
                Logger.instance().debug("ToolWrapper not ready: rule: " + tool_wrapper.rule_name + " -> " + str(tool_wrapper.tool_python_path))
                # The buffer contains the ToolWrappers that have inputs which are not ready yet.
                self.__list_queue_buffer.append(tool_wrapper_thread)

        Logger.instance().debug("Buffer: " + str(["rule: " + t.get_toolwrapper().rule_name + "->" +
                                                  t.get_toolwrapper().tool_python_path for t in self.__list_queue_buffer]))
        Logger.instance().debug("Running rules: " + str(self.__count_exec))

        # There is no more ToolWrapper that are waiting to be executed.
        # Is there some tools that are currently being executed?
        if self.__count_exec == 0:
            # Is there some tools that weren't ready?
            finish_epoch_millis_unix_ms, finish_epoch_millis_datetime = get_current_time()
            if len(self.__list_queue_buffer) == 0:
                # If there is no tool waiting and no tool being executed, the workflow has finished.
                # finished_at = finish_epoch_millis_unix_ms
                # finished_at_strftime = datetime.datetime.fromtimestamp(finished_at/1000).strftime('%Y-%m-%d %H:%M:%S')
                Logger.instance().info("The workflow has completed. Finished at: {}".format(finish_epoch_millis_datetime))
                self.set_finishing_informations(finish_epoch_millis_datetime, "FINISHED")
                SQLManager.instance().get_session().close()
                sys.exit(0)
            # uniquement en environnement multiThreadpredece
            elif not self.check_buffer():
                # If there is no tool being executed but there is that are waiting something, the workflow has an issue
                # finished_at = time_unix_ms()
                tw_list = [t.get_toolwrapper() for t in self.__list_queue_buffer]
                if len(tw_list) > 0:
                    input_files_not_ready = tw_list[0].get_input_files_not_ready()
                    self.set_finishing_informations(finish_epoch_millis_datetime, "ERROR")
                    raise WopMarsException("The workflow has failed.",
                                           " The inputs '{}' have failed for this tool '{}'"
                                           .format(input_files_not_ready[0], tw_list[0].rule_name))
            # If there is one tool that is ready, it means that it is in queue because ressources weren't available.

    def set_finishing_informations(self, finished_at, status):
        """
        Set the finsihing information of the whole workflow.

        :param finished_at: The finishing human time
        :type finished_at: DateTime
        :param status: The final status of the workflow
        :type status: str
        """

        execution = self.__session.query(Execution).order_by(Execution.id.desc()).first()

        # for tool_wrapper in set(self.__dag_to_exec.nodes()):
        #     if tool_wrapper.status == 'ALREADY_EXECUTED' or tool_wrapper.status == 'ERROR':
        #         self.__session.delete(tool_wrapper)
        #         self.__session.commit()

        ######################################################################################
        #
        # Delete execution if execution ALL tool_wrappers where skipped
        # that is ALL tool_wrappers of this execution have status == ALREADY_EXECUTED
        #
        ######################################################################################

        execution_tool_wrapper_count = self.__session.query(ToolWrapper).filter(
            ToolWrapper.execution_id == execution.id).count()
        execution_tool_wrapper_already_executed_count = self.__session.query(ToolWrapper)\
            .filter(ToolWrapper.execution_id == execution.id)\
            .filter(ToolWrapper.status == 'ALREADY_EXECUTED').count()

        if execution_tool_wrapper_count == execution_tool_wrapper_already_executed_count:
            self.__session.delete(execution)
            self.__session.commit()

        ######################################################################################
        #
        # Delete execution if --dry-run
        #
        ######################################################################################

        elif OptionManager.instance()["--dry-run"]:
            # pass
            self.__session.delete(execution)
            self.__session.commit()

        ######################################################################################
        #
        # If NOT all tool_wrappers skipped AND NOT --dry-run, update finished time
        #
        ######################################################################################

        else:  # not --dry-run, update finishing time

            if execution is not None:
                execution.finished_at = finished_at
                execution.time = int((execution.finished_at - execution.started_at).total_seconds())
                execution.status = status
                self.__session.add(execution)
                self.__session.commit()

    def all_predecessors_have_run(self, rule):
        """
        Check if all the predecessors of the given tool_python_path have yet been executed in this workflow.

        :param rule: Node of the DAG
        :type rule: :class:`~.wopmars.main.framework.database.models.ToolWrapper.ToolWrapper`
        :return: Bool
        """
        return bool(self.__dag_to_exec.get_all_predecessors(rule).difference(set([rule])).issubset(set(self.__already_runned)))

    @staticmethod
    def is_this_tool_wrapper_already_executed(tool_wrapper):
        """
        Check if this tool wrapper is already executed.

        The conditions are:
            - The tool_wrapper outputs exist
            - The tool_wrapper outputs are more recent than inputs
            - If tool_wrapper exist in the database, then it checks if there are the same parameter values

        :param tool_wrapper: The tool_wrapper to be tested
        :type tool_wrapper: :class:`~.wopmars.models.ToolWrapper.ToolWrapper`
        """
        session = SQLManager.instance().get_session()

        # Get latest tool_wrapper
        # same_rule_list = session.query(ToolWrapper).filter(ToolWrapper.tool_python_path == tool_wrapper.tool_python_path)\
        #     .filter(ToolWrapper.execution_id != tool_wrapper.execution_id).all()
        # i = 0
        # while i < len(same_rule_list):
        #     same = False
        #     # two tool_wrapper are equals if they have the same parameters, the same file names and path
        #     # and the same table names and models
        #     if same_rule_list[i] == tool_wrapper and \
        #             same_rule_list[i].does_output_exist() and \
        #             same_rule_list[i].is_output_more_recent_than_input():
        #             same = True
        #     if not same:
        #         del same_rule_list[i]
        #     else:
        #         i += 1

        # # The elements of the list have been removed if none fit the conditions
        # return bool(same_rule_list)

        # return tool_wrapper == tool_wrapper_old \
        #        and tool_wrapper_old.does_output_exist() \
        #        and tool_wrapper_old.is_output_more_recent_than_input()

        is_already_executed = False  # Default, not executed

        # Check if output of tool_wrapper exist and output is more recent than input
        is_already_executed = tool_wrapper.output_file_exists() and tool_wrapper.output_table_exists() \
                           and tool_wrapper.is_output_more_recent_than_input()

        tool_wrapper_old = session.query(ToolWrapper).filter(ToolWrapper.tool_python_path == tool_wrapper.tool_python_path)\
            .filter(ToolWrapper.execution_id != tool_wrapper.execution_id)\
            .order_by(ToolWrapper.id.desc()).first()

        if not (tool_wrapper_old is None):  # If tool_wrapper exists in the database, check if same parameter values

            is_already_executed = is_already_executed and (tool_wrapper == tool_wrapper_old)

        return is_already_executed

    def check_buffer(self):
        """
        Check if the buffer contains ToolWrapper that are ready.

        :return: bool: True if there is at least one tool_python_path that is READY in the buffer.
        """
        for tw in self.__list_queue_buffer:
            if tw.get_toolwrapper().get_state() == ToolWrapper.READY:
                return True
        return False

    def notify_success(self, thread_toolwrapper):
        """
        Handle thread_toolwrapper success by continuing the dag.

        :param thread_toolwrapper: ToolWrapper thread that just succeed
        :type thread_toolwrapper: :class:`~.wopmars.management.ToolWrapperThread.ToolWrapperThread`
        """
        self.__session.add(thread_toolwrapper.get_toolwrapper())
        self.__session.commit()

        dry_status = thread_toolwrapper.get_dry()
        # if not OptionManager.instance()["--dry-run"]:
        #     thread_toolwrapper.get_toolwrapper().set_args_time_and_size("output", dry_status)
        if dry_status is False and not OptionManager.instance()["--dry-run"]:
            Logger.instance().info("ToolWrapper {} -> {} has succeeded."
                                   .format(str(thread_toolwrapper.get_toolwrapper().rule_name),
                                           str(thread_toolwrapper.get_toolwrapper().__class__.__name__)))
        # Continue the dag execution from the tool_python_path that just finished.
        self.__already_runned.add(thread_toolwrapper.get_toolwrapper())
        self.__count_exec -= 1

        if len(self.__list_queue_buffer):
            Logger.instance().debug("Fill the queue with the buffer: " +
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
