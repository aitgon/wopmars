"""
Module containing the RuleThread class.
"""
import errno
import threading
import os
import traceback

from wopmars.SQLManager import SQLManager
from wopmars.Observable import Observable
from wopmars.utils.Logger import Logger
from wopmars.utils.OptionManager import OptionManager
from wopmars.utils.exceptions.WopMarsException import WopMarsException
from wopmars.utils.various import get_mtime, get_current_time


class RuleThread(threading.Thread, Observable):
    """
    The class RuleThread is a wrapper for executing toolwrappers.

    It has been designed in order to implement the multithreading, this is why it inherit from threading.Thread.
    """

    def __init__(self, rule):
        """
        self.__dry = True means that the tool shouldn't be executed because its output already exist

        :return:
        """
        threading.Thread.__init__(self)
        self.__set_observer = set([])
        # the wrapped tool_python_path
        self.__rule = rule
        #self.__dry is different than the --dry-run option because it says "this has already been executed" whereas
        # the --dry-run option means "simulate the whole execution"
        # self.__dry can be True even if the --dry-run mode is enabled: it means "this tool has already its output, you
        # don't even need to simulate execution, just skip"
        self.__dry = False

    def get_toolwrapper(self):
        return self.__rule

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
            self.__rule.set_session(wopmars_session)
            # if the tool need to be executed because its output doesn't exist
            if not self.__dry:
                Logger.instance().info(
                    "\n" + str(self.__rule) + "\n" + "command line: \n\t" + self.get_command_line())
                # if you shouldn't simulate
                if not OptionManager.instance()["--dry-run"]:
                    Logger.instance().info("Rule: " + str(self.__rule.name) + " -> " + self.__rule.__class__.__name__ + " started.")
                    # mkdir -p output dir: before running we need output dir
                    output_file_fields = self.__rule.specify_output_file()
                    for out_field in output_file_fields:
                        out_file_path = self.__rule.output_file(out_field)
                        out_dir = os.path.dirname(out_file_path)
                        try:
                            os.makedirs(out_dir)
                        except OSError as exception:
                            if exception.errno != errno.EEXIST:
                                raise
                    # end of mkdir -p output dir
                    self.__rule.run()
                    wopmars_session.commit()
                    time_unix_ms, time_human = get_current_time()
                    self.__rule.set_execution_infos(start, time_human, "EXECUTED")
                else:
                    Logger.instance().debug("Dry-run mode enabled. Execution skiped.")
                    self.__rule.set_execution_infos(status="DRY")
            else:
                Logger.instance().info("Rule: " + str(self.__rule.name) + " -> " + self.__rule.__class__.__name__ + " skiped.")
                self.__rule.set_execution_infos(start, time_human, "ALREADY_EXECUTED")
        except Exception as e:
            wopmars_session.rollback()
            self.__rule.set_execution_infos(start, time_human, "EXECUTION_ERROR")
            raise WopMarsException("Error while executing rule " + self.__rule.name +
                                   " (Rule " + self.__rule.tool_python_path + ")",
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
        list_str_inputs_files = [f.name + "': '" + f.path for f in self.__rule.files if f.type.is_input == 1]
        list_str_inputs_tables = [t.tablename + "': '" + t.model_py_path for t in self.__rule.tables if t.type.is_input == 1]
        str_input_dict = ""
        str_input_dict_files = ""
        str_input_dict_tables = ""

        if list_str_inputs_files:
            str_input_dict_files = "'file':{'" + "', '".join(list_str_inputs_files) + "'}"
        if list_str_inputs_tables:
            str_input_dict_tables = "'table':{'" + "', '".join(list_str_inputs_tables) + "'}"
        if list_str_inputs_files or list_str_inputs_tables:
            str_input_dict = " -i \"{%s}\"" % (", ".join([s for s in [str_input_dict_files, str_input_dict_tables] if s != ""]))

        list_str_outputs_files = [f.name + "': '" + f.path for f in self.__rule.files if f.type.is_input == 0]
        list_str_outputs_tables = [t.tablename + "': '" + t.model_py_path for t in self.__rule.tables if t.type.is_input == 0]
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
        s += "wopmars tool " + self.__rule.tool_python_path + str_input_dict + str_output_dict + str_params_dict + " " + \
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
        return self.__rule == other.get_toolwrapper()

    def __hash__(self):
        return id(self)
