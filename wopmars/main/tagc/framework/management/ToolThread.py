"""
Module containing the ToolThread class.
"""
import datetime
import threading

import time

from wopmars.main.tagc.framework.bdd.SQLManager import SQLManager
from wopmars.main.tagc.framework.management.Observable import Observable
from wopmars.main.tagc.utils.Logger import Logger
from wopmars.main.tagc.utils.OptionManager import OptionManager


class ToolThread(threading.Thread, Observable):
    """
    class ToolThread
    """

    def __init__(self, toolwrapper):
        """
        

        :return:
        """
        threading.Thread.__init__(self)
        self.__set_observer = set([])
        self.__toolwrapper = toolwrapper
        self.__dry = False

    def get_toolwrapper(self):
        return self.__toolwrapper

    def set_dry(self, dry):
        self.__dry = dry

    def get_dry(self):
        return self.__dry

    def run(self):
        """
        Run the tool and fire events.
        :return:
        """

        session_tw = SQLManager.instance().get_session()
        start = datetime.datetime.fromtimestamp(time.time())
        try:
            self.__toolwrapper.set_session(session_tw)
            if not self.__dry:
                Logger.instance().info(
                    "\n" + str(self.__toolwrapper) + "\n" + "command line: \n\t" + self.get_command_line())
                if not OptionManager.instance()["--dry-run"]:
                    Logger.instance().info("Rule: " + str(self.__toolwrapper.name) + " -> " + self.__toolwrapper.__class__.__name__ + " started.")
                    self.__toolwrapper.run()
                    session_tw.commit()
                    self.__toolwrapper.set_execution_infos(start, datetime.datetime.fromtimestamp(time.time()), "EXECUTED")
                else:
                    Logger.instance().debug("Dry-run mode enabled. Execution skiped.")
                    self.__toolwrapper.set_execution_infos(status="DRY")
            else:
                Logger.instance().info("Rule: " + str(self.__toolwrapper.name) + " -> " + self.__toolwrapper.__class__.__name__ + " skiped.")
                self.__toolwrapper.set_execution_infos(start, datetime.datetime.fromtimestamp(time.time()), "ALREADY_EXECUTED")
        except Exception as e:
            session_tw.rollback()
            self.__toolwrapper.set_execution_infos(start, datetime.datetime.fromtimestamp(time.time()), "EXECUTION_ERROR")
            raise e
        finally:
            # todo twthread , fermer session
            # session_tw.close()
            pass
        self.fire_success()

    def get_command_line(self):
        list_str_inputs_files = [f.name + "': '" + f.path for f in self.__toolwrapper.files if f.type.name == "input"]
        list_str_inputs_tables = [t.tablename + "': '" + t.model for t in self.__toolwrapper.tables if t.type.name == "input"]
        str_input_dict = ""
        str_input_dict_files = ""
        str_input_dict_tables = ""

        if list_str_inputs_files:
            str_input_dict_files = "'file':{'" + "', '".join(list_str_inputs_files) + "'}"
        if list_str_inputs_tables:
            str_input_dict_tables = "'table':{'" + "', '".join(list_str_inputs_tables) + "'}"
        if list_str_inputs_files or list_str_inputs_tables:
            str_input_dict = " -i \"{%s}\"" % (", ".join([s for s in [str_input_dict_files, str_input_dict_tables] if s != ""]))

        list_str_outputs_files = [f.name + "': '" + f.path for f in self.__toolwrapper.files if f.type.name == "output"]
        list_str_outputs_tables = [t.tablename + "': '" + t.model for t in self.__toolwrapper.tables if t.type.name == "output"]
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
        s += "wopmars tool " + self.__toolwrapper.toolwrapper + str_input_dict + str_output_dict + str_params_dict + " " + \
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
        return self.__toolwrapper == other.get_toolwrapper()

    def __hash__(self):
        return id(self)