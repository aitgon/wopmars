"""
Module containing the ToolWrapperThread class.
"""
import pathlib
import threading
import os
import traceback

from wopmars.SQLManager import SQLManager
from wopmars.Observable import Observable
from wopmars.utils.Logger import Logger
from wopmars.utils.OptionManager import OptionManager
from wopmars.utils.WopMarsException import WopMarsException
from wopmars.utils.various import get_current_time


class ToolWrapperThread(threading.Thread, Observable):
    """
    The class ToolWrapperThread is a wrapper for executing toolwrappers.

    It has been designed in order to implement the multithreading, this is why it inherit from threading.Thread.
    """

    def __init__(self, tool_wrapper):
        """
        self.__dry = True means that the tool shouldn't be executed because its output already exist

        :return:
        """
        threading.Thread.__init__(self)
        self.__set_observer = set([])
        # the wrapped tool_python_path
        self.__tool_wrapper = tool_wrapper
        #self.__dry is different than the --dry-run option because it says "this has already been executed" whereas
        # the --dry-run option means "simulate the whole execution"
        # self.__dry can be True even if the --dry-run mode is enabled: it means "this tool has already its output, you
        # don't even need to simulate execution, just skip"
        self.__dry = False

    def get_toolwrapper(self):
        return self.__tool_wrapper

    def set_dry(self, dry):
        self.__dry = dry

    def get_dry(self):
        return self.__dry

    def run(self):
        """
        Run the tool and fire events.
        :return:
        """

        wopmars_session = SQLManager.instance().get_session()
        time_unix_ms, time_human = get_current_time()
        start = time_human
        try:
            # self.__tool_wrapper.set_session(wopmars_session)
            self.__tool_wrapper.session = wopmars_session
            # if the tool need to be executed because its output doesn't exist
            if self.__dry:  # tool_wrapper skipped
                Logger.instance().info("ToolWrapper skipped: {} -> {}"
                                       .format(self.__tool_wrapper.rule_name, self.__tool_wrapper.__class__.__name__))
                # Logger.instance().info("ToolWrapper: " + str(self.__tool_wrapper.rule_name) +
                #                        " -> " + self.__tool_wrapper.__class__.__name__ + " skipped.")
                self.__tool_wrapper.set_execution_infos(start, time_human, "ALREADY_EXECUTED")
            else:
                Logger.instance().info(
                    "\n" + str(self.__tool_wrapper) + "\n" + "command line: \n\t" + self.get_command_line())
                # if you shouldn't simulate
                if OptionManager.instance()["--dry-run"]:  # dry run
                    Logger.instance().debug("Dry-run mode enabled. Execution skipped.")
                    self.__tool_wrapper.set_execution_infos(status="DRY")
                else:  # normal execution
                    # if OptionManager.instance()["--touch"]:  # dry run
                    #     Logger.instance().debug("Touch mode enabled.")
                    #     self.__tool_wrapper.touch()
                    Logger.instance().info("ToolWrapper: " + str(self.__tool_wrapper.rule_name) + " -> "
                                           + self.__tool_wrapper.__class__.__name__ + " started.")
                    output_file_fields = self.__tool_wrapper.specify_output_file()
                    for out_field in output_file_fields:
                        out_file_path = self.__tool_wrapper.output_file(out_field)
                        out_dir = os.path.dirname(out_file_path)
                        pathlib.Path(out_dir).mkdir(parents=True, exist_ok=True)

                    ####################################################################################################
                    #
                    # Touch output files of tool wrapper
                    #
                    ####################################################################################################

                    if OptionManager.instance()["--touch"]:  # Just touch
                        self.__tool_wrapper.touch()

                    ####################################################################################################
                    #
                    # Normal run of tool wrapper
                    #
                    ####################################################################################################

                    else:  # Run
                        self.__tool_wrapper.run()
                    wopmars_session.commit()
                    time_unix_ms, time_human = get_current_time()
                    self.__tool_wrapper.set_execution_infos(start, time_human, "EXECUTED")

        except Exception as e:
            wopmars_session.rollback()
            self.__tool_wrapper.set_execution_infos(start, time_human, "ERROR")
            raise WopMarsException("Error while executing rule " + self.__tool_wrapper.rule_name +
                                   " (ToolWrapper " + self.__tool_wrapper.tool_python_path + ")",
                                   "Full stack trace: \n" + str(traceback.format_exc()))
        finally:
            # todo twthread , fermer session
            # session_tw.close()
            pass
        self.fire_success()

    def get_command_line(self):
        """
        This create a string containing the command line for executing the tool_python_path only.

        :return: The string containg the command line
        """
        list_str_inputs_files = [f.file_key + "': '" + f.path for f in self.__tool_wrapper.relation_toolwrapper_to_fileioinfo if f.relation_file_or_tableioinfo_to_typeio.is_input == 1]
        list_str_inputs_tables = [t.table_key + "': '" + t.model_py_path for t in self.__tool_wrapper.relation_toolwrapper_to_tableioinfo if t.relation_file_or_tableioinfo_to_typeio.is_input == 1]
        str_input_dict = ""
        str_input_dict_files = ""
        str_input_dict_tables = ""

        if list_str_inputs_files:
            str_input_dict_files = "'file':{'" + "', '".join(list_str_inputs_files) + "'}"
        if list_str_inputs_tables:
            str_input_dict_tables = "'table':{'" + "', '".join(list_str_inputs_tables) + "'}"
        if list_str_inputs_files or list_str_inputs_tables:
            str_input_dict = " -i \"{%s}\"" % (", ".join([s for s in [str_input_dict_files, str_input_dict_tables] if s != ""]))

        list_str_outputs_files = [f.file_key + "': '" + f.path for f in self.__tool_wrapper.relation_toolwrapper_to_fileioinfo if f.relation_file_or_tableioinfo_to_typeio.is_input == 0]
        list_str_outputs_tables = [t.table_key + "': '" + t.model_py_path for t in self.__tool_wrapper.relation_toolwrapper_to_tableioinfo if t.relation_file_or_tableioinfo_to_typeio.is_input == 0]
        str_output_dict = ""
        str_output_dict_files = ""
        str_output_dict_tables = ""

        if list_str_outputs_files:
            str_output_dict_files = "'file':{'" + "', '".join(list_str_outputs_files) + "'}"
        if list_str_outputs_tables:
            str_output_dict_tables = "'table':{'" + "', '".join(list_str_outputs_tables) + "'}"
        if list_str_outputs_files or list_str_outputs_tables:
            str_output_dict = " -o \"{%s}\"" % (", ".join([s for s in [str_output_dict_files, str_output_dict_tables] if s != ""]))

        list_str_params = []
        str_params_dict = ""

        if list_str_params:
            str_params_dict = " -P \"{'" + "', '".join(list_str_params) + "'}\""

        consistent_keys = ["--forceall", "--dot", "--log", ]
        s = ""
        s += "wopmars tool " + self.__tool_wrapper.tool_python_path + str_input_dict + str_output_dict + str_params_dict + " " + \
             " ".join(str(key) + " " + str(OptionManager.instance()[key]) for key in OptionManager.instance().keys() if key in consistent_keys and OptionManager.instance()[key] is not None and type(OptionManager.instance()[key]) != bool) + \
             " " + " ".join(str(key) for key in OptionManager.instance().keys() if key in consistent_keys and OptionManager.instance()[key] is True and type(OptionManager.instance()[key]) == bool)

        return s

    def get_observers(self):
        """
        Return the set of observers.

        :return: set observers
        """
        return self.__set_observer

    def subscribe(self, obs):
        """
        An observer subscribes to the obervable.

        :param obs:
        :return:
        """
        self.__set_observer.add(obs)

    def fire_failure(self):
        """
        Notify all ToolWrapperObservers that the execution has failed.

        :return:
        """
        for obs in self.get_observers():
            obs.notify_failure(self)

    def fire_success(self):
        """
        Notify all ToolWrapperObservers that the run has suceeded

        :return:
        """
        for obs in self.get_observers():
            obs.notify_success(self)

    def __eq__(self, other):
        assert isinstance(other, self.__class__)
        return self.__tool_wrapper == other.get_toolwrapper()

    def __hash__(self):
        return id(self)
