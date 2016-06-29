"""
This module contains the ToolWrapper class
"""
import datetime
import os

import time
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from src.main.fr.tagc.wopmars.framework.bdd.Base import Base
from src.main.fr.tagc.wopmars.framework.bdd.SQLManager import SQLManager
from src.main.fr.tagc.wopmars.framework.bdd.tables.Execution import Execution
from src.main.fr.tagc.wopmars.framework.bdd.tables.IODbPut import IODbPut
from src.main.fr.tagc.wopmars.utils.Logger import Logger
from src.main.fr.tagc.wopmars.utils.exceptions.WopMarsException import WopMarsException


class ToolWrapper(Base):
    """
    The class ToolWrapper is the superclass of the Wrapper which
    will be designed by the wrapper developers.
    """

    __tablename__ = "wom_rule"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    toolwrapper = Column(String)
    execution_id = Column(Integer, ForeignKey("wom_execution.id"))

    # One rule has Many table
    tables = relationship("IODbPut", back_populates="rule")
    # One rule has Many file
    files = relationship("IOFilePut", back_populates="rule")
    # One rule has Many option
    options = relationship("Option", back_populates="rule")
    # One rule has one execution
    execution = relationship("Execution", back_populates="rules")

    # parentrules = relationship etc...
    __mapper_args__ = {
        'polymorphic_on': toolwrapper,
        'polymorphic_identity': 'ToolWrapper'
    }

    NEW = 1
    READY = 2
    NOT_READY = 3

    def __init__(self, rule_name=""):
        """
        The constructor of the toolwrapper, must not be overwritten.

        set_observer is the set of all observers of the toolwrappers.
        input_file_dict is the dict containing the IOFilePut objects of the file input of the toolwrapper.
        option_dict is the dict containing the Option objects of the params of the toolwrapper.
        output_file_dict is the dict containing the IOFilePut objects of the file output of the toolwrapper.
        state is the constant refering to the state of the toolwrapper, it is initialized at "NEW"

        :param input_file_dict: dict(String: IOPUT)
        :param output_file_dict: dict(String: IOPUT)
        :param option_dict: dict(String: Option)
        :return: void
        """
        super().__init__(name=rule_name)
        # int
        self.__state = ToolWrapper.NEW
        # <WopMarsSession>
        self.__session = None


    ### PARSING METHODS

    def is_content_respected(self):
        """
        This method checks if the parameters dictionary are properly formed, according to the specifications of the
        wrapper developer.

        :return:
        """

        # the options have to be checked first because they can alter the behavior of the is_input_respected and
        # is_output_respected methods
        self.is_options_respected()

        self.is_input_respected()
        self.is_output_respected()

    def is_input_respected(self):
        """
        Check if the input dictionary given in the constructor is properly formed for the tool.

        It checks if the output variable names exists or not.
        If not, throws a WopMarsParsingException(3)
        :return:void
        """
        set_input_file_names = set([f_input.name for f_input in self.files if f_input.type.name == "input"])
        if  set_input_file_names != set(self.get_input_file()):
            raise WopMarsException("The content of the definition file is not valid.",
                                   "The given input variable's names for " + self.__class__.__name__ +
                                   " are not correct, they should be: " +
                                   "\n\t'{0}'".format("'\n\t'".join(self.get_input_file())) +
                                   "\n" + "They are:" +
                                   "\n\t'{0}'".format("'\n\t'".join(set_input_file_names))
                                   )

    def is_output_respected(self):
        """
        Check if the output dictionary given in the constructor is properly formed for the tool.

        It checks if the output variable names exists or not. Throws WopMarsParsingException if not
        :return:void
        """
        if set([f_output.name for f_output in self.files if f_output.type.name == "output"]) != set(self.get_output_file()):
            raise WopMarsException("The content of the definition file is not valid.",
                                   "The given output variable names for " + self.__class__.__name__ +
                                   " are not correct, they should be: " +
                                   "\n\t'{0}'".format("'\n\t'".join(self.get_output_file())) +
                                   "\n" + "They are:" +
                                   "\n\t'{0}'".format("'\n\t'".join([f.name for f in self.files if f.type.name == "output"]))
                                   )

    def is_options_respected(self):
        """
        This method check if the params given in the constructor are properly formed for the tool.

        It checks if the params names given by the user exists or not, if the type correspond and if the required
        options are given
        :return:
        """
        dict_wrapper_opt_carac = self.get_params()

        # check if the given options are authorized
        if not set([opt.name for opt in self.options]).issubset(dict_wrapper_opt_carac):
            raise WopMarsException("The content of the definition file is not valid.",
                                   "The given option variable for " + self.__class__.__name__ +
                                   " are not correct, they should be in: " +
                                   "\n\t'{0}'".format("'\n\t'".join(dict_wrapper_opt_carac)) +
                                   "\n" + "They are:" +
                                   "\n\t'{0}'".format("'\n\t'".join([opt.name for opt in self.options]))
                                   )

        # check if the types correspond
        for opt in self.options:
            opt.correspond(dict_wrapper_opt_carac[opt.name])

        # check if the required options are given
        for opt in dict_wrapper_opt_carac:
            if "required" in dict_wrapper_opt_carac[opt].lower() and opt not in [opt2.name for opt2 in self.options]:
                raise WopMarsException("The content of the definition file is not valid.",
                                       "The option " + opt + " has not been provided but it is required.")

    def follows(self, other):
        """
        Check whether the "other" follows "self" in the execution DAG.

        Check whether "other" has one output value in "self" possible input values.
        The output value are given from the Relationnal mapping between toolwrappers and related objects:
        * IODbPut
        * IOFilePut

        :param other: ToolWrapper that is a predecessor of "self"
        :return: bool True if "self" follows "other"
        """
        for rule_f_path in [f.path for f in self.files if f.type.name == "input"]:
            for rule_f2_path in [f.path for f in other.files if f.type.name == "output"]:
                if rule_f_path == rule_f2_path:
                    return True

        for rule_t_name in [t.name for t in self.tables if t.type.name == "input"]:
            for rule_t2_name in [t.name for t in other.tables if t.type.name == "output"]:
                if rule_t_name == rule_t2_name:
                    return True

        return False

    ### Workflow Manager methods

    def are_inputs_ready(self):
        """
        Check if inputs are ready

        :return: bool - True if inputs are ready.
        """
        input_files = [f for f in self.files if f.type.name == "input"]
        input_tables = [t for t in self.tables if t.type.name == "input"]
        inputs = input_files + input_tables
        Logger.instance().debug("Inputs of " + str(self.__class__.__name__) + ": " + str([i.name for i in inputs]))
        for i in inputs:
            if not i.is_ready():
                Logger.instance().debug("Input: " + str(i.name) + " is not ready.")
                self.__state = ToolWrapper.NOT_READY
                return False
            Logger.instance().debug("Input: " + str(i.name) + " is ready.")

        self.__state = ToolWrapper.READY
        return True

    def set_args_date_and_size(self, type, dry=False):
        """
        The date and the size of IOPut elements are set (if needed).

        The date and the size of the files are set according to the actual date of last modification and size of the system files

        The date of the tables are set according to the date of last modification notified in the modification_table table
        If the type of IOPut is "output" and the execution is "not dry", the date in modification_table is set to the
        current time.time() datetime.

        :param type: String "input" or "output"
        :param dry: Bool (True or False)
        :return:
        """
        session = SQLManager.instance().get_session()
        for f in [f for f in self.files if f.type.name == type]:
            date = datetime.datetime.fromtimestamp(os.path.getmtime(f.path))
            size = os.path.getsize(f.path)
            f.used_at = date
            f.size = size
            session.add(f)
            if type == "input":
                Logger.instance().debug("Input file " + str(f) + " used.")
            elif type == "output" and dry:
                Logger.instance().debug("Output file " + str(f) + " has been loaded from previous execution.")
            elif type == "output" and not dry:
                Logger.instance().debug("Output file " + str(f) + " has been created.")
        # this commit is due to a bug that i couldn't figure out: the session empty itself between the two loops...
        # this is not good at all since it may lead to inconsistence in the bdd
        # todo fix
        session.commit()

        for t in [t for t in self.tables if t.type.name == type]:
            if type == "output" and not dry:
                Logger.instance().debug("Output table " + str(t) + " has been modified.")
                t.modification.date = datetime.datetime.fromtimestamp(time.time())
            elif type == "output" and dry:
                Logger.instance().debug("Output table " + str(t) + " not modified because of dry run.")
            elif type == "input":
                Logger.instance().debug("Input table " + str(t) + " used.")
            t.used_at = t.modification.date
            session.add(t)
        session.commit()

    def same_input_than(self, other):
        """
        Check if the other ToolWrapper have the same input than self.

        The input are say "the same" if:
            - The tables have the same name and the same last modifcation datetime
            - The file have the same name, the same lastm mdoficiation datetime and the same size
        :param other:
        :return:
        """
        for t in [t for t in self.tables if t.type.name == "input"]:
            is_same = False
            for t2 in [t2 for t2 in other.tables if t2.type.name == "input"]:
                if (t.name == t2.name and
                       t.used_at == t2.used_at):
                    is_same = True
                    break
            if not is_same:
                return False

        for f in [f for f in self.files if f.type.name == "input"]:
            is_same = False
            for f2 in [f2 for f2 in other.files if f2.type.name == "input"]:
                # todo refactorer pour rassembler la boucle et la condition
                if (f.name == f2.name and
                        f.path == f2.path and
                        f.used_at == f2.used_at and
                        f.size == f2.size):
                    is_same = True
                    break
            if not is_same:
                return False
        return True

    def is_output_ok(self):
        """
        Check if the output of self are ready to use.

        What is checked:
            -for files:
                - They exists
                - Their size and date are not None
                - Their date are after all input dates
                - Their size and date in bdd are the same than the real ones

            - for tables:
                - They exists
                - Their date are after all input dates
                - Their date are the same in table 'table' than in 'modification_table'
        :return:
        """
        # todo tester ça, je ne pense pas que ca fonctionne, en fin de compte
        for of in [f for f in self.files if f.type.name == "output"]:
            if not os.path.exists(of.path) or \
                    not all(of.used_at > in_ft.used_at for in_ft in self.files + self.tables if (in_ft.type.name == "input" and
                                                                                                 of.used_at is not None and
                                                                                                 in_ft.used_at is not None)) or \
                    not (of.size == os.path.getsize(of.path) and of.used_at == datetime.datetime.fromtimestamp(os.path.getmtime(of.path))):
                return False

        for ot in [t for t in self.tables if t.type.name == "output"]:
            if not all(ot.used_at > in_ft.used_at for in_ft in self.files + self.tables if (in_ft.type.name == "input" and
                                                                                            ot.used_at is not None and
                                                                                            in_ft.used_at is not None)) or \
                    not (ot.used_at == ot.modification.date):
                return False
        return True

    def get_state(self):
        return self.__state

    def get_input_file_dict(self):
        """
        Return the dict of input_files:

        :return: Dict: <String>INPUTNAME : <IOFilePut>INPUT
        """
        return self.__input_file_dict

    def get_output_file_dict(self):
        """
        Return the dict of output_files:

        :return: Dict: <String>OUTPUTNAME : <IOFilePut>OUTPUT
        """
        return self.__output_file_dict

    def get_input_table_dict(self):
        """
        Return the dict of input_tables:

        :return: Dict: <String>INPUTNAME : <IODbPut>INPUT
        """
        return self.__input_table_dict

    def get_output_table_dict(self):
        """
        Return the dict of output_tables:

        :return: Dict: <String>OUTPUTNAME : <IODbPut>OUTPUT
        """
        return self.__output_table_dict

    def get_option_dict(self):
        return self.__option_dict

    def set_session(self, session):
        self.__session = session

    def __eq__(self, other):
        """
        Two ToolWrapper objects are equals if all their attributes are equals
        :param other: ToolWrapper
        :return:
        """
        return (isinstance(other, self.__class__) and
                self.same_files(other, "input") and
                self.same_tables(other, "input") and
                self.same_files(other, "output") and
                self.same_tables(other, "output") and
                self.same_options(other))

    # todo check size / date -> non! pour le moment on vérifie juste que les paramètres sont identiques
    def same_files(self, other, type_name):
        for input_f in [rf for rf in self.files if rf.type.name == type_name]:
            is_in = bool([rf for rf in other.files if (os.path.abspath(input_f.path) == os.path.abspath(rf.path) and
                                                       input_f.name == rf.name and
                                                       rf.type.name == type_name)])
            if not is_in:
                return False
        return True

    # todo check_content? -> dans le == des IODbPut
    def same_tables(self, other, type_name):
        for input_t in [t for t in self.tables if t.type.name == type_name]:
            is_in = bool([t for t in other.tables if (input_t.name == t.name and
                                                      t.type.name == type_name)])
            if not is_in:
                return False
        return True

    def same_options(self, other):
        for opt in self.options:
            is_in = bool([o for o in other.options if (o.name == opt.name and
                                                       o.value == opt.value)])

            if not is_in:
                return False
        return True

    def __hash__(self):
        """
        Redefining the hash method allows ToolWrapper objects to be indexed in sets and dict
        :return:
        """
        return id(self)

    def __repr__(self):
        """
        Return the string representing the toolwrapper in the DAG.

        :return: String representing the toolwrapper
        """
        s = "\""
        s += self.name
        s += "\\n"
        s += "tool: " + self.__class__.__name__
        s += "\\n"
        for input_f in [f for f in self.files if f.type.name == "input"]:
            s += "\\n\t\t" + input_f.name + ": " + str(input_f.path)
        for input_t in [t for t in self.tables if t.type.name == "input"]:
            s += "\\n\t\tinput_table: " + input_t.name
        s += "\\n"
        for output_f in [f for f in self.files if f.type.name == "output"]:
            s += "\\n\t\t" + output_f.name + ": " + str(output_f.path)
        for output_t in [t for t in self.tables if t.type.name == "output"]:
            s += "\\n\t\toutput_table: " + output_t.name
        s += "\""
        return s

    # ###### Method that worker developper should implement#######

    def get_input_file(self):
        return []

    def get_input_table(self):
        return []

    def get_output_file(self):
        return []

    def get_output_table(self):
        return []

    def get_params(self):
        return {}

    def run(self):
        pass

    ### Methods availables for the tool developer

    def input_file(self, key):
        """
        Return the path of the specified input file.

        :param key: String the name of the variable containing the path
        :return:
        """
        return [f.path for f in self.files if f.name == key and f.type.name == "input"][0]

    def input_table(self, key):
        """
        Return the input table object of the given name.

        :param key: String: the name of the Table object.
        :return:
        """
        return [t for t in self.tables if t.name == key and t.type.name == "input"][0].get_table()

    # todo exception erreur speciale developpeur métier (aide au debogage)
    def output_file(self, key):
        """
        Return the path of the specified output file.

        :param key: String the name of the variable containing the path
        :return:
        """
        return [f.path for f in self.files if f.name == key and f.type.name == "output"][0]

    def output_table(self, key):
        """
        Return the output table object of the given name.

        :param key: String: the name of the Table object.
        :return:
        """
        return [t for t in self.tables if t.name == key and t.type.name == "output"][0].get_table()

    def option(self, key):
        return [o.value for o in self.options if o.name == key][0]

    def session(self):
        return self.__session
