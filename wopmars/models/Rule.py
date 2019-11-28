import os

from sqlalchemy import Column, Integer, String, ForeignKey, Float, BigInteger, DateTime
from sqlalchemy.orm import relationship

from wopmars.Base import Base
from wopmars.SQLManager import SQLManager
from wopmars.models.Option import Option
from wopmars.utils.Logger import Logger
from wopmars.utils.OptionManager import OptionManager
from wopmars.utils.exceptions.WopMarsException import WopMarsException
from wopmars.utils.various import get_mtime, get_current_time


class Rule(Base):
    """
    The class Rule is the superclass of the wrappers which will be designed by the wrapper developers. It is the
    SQLAlchemy Model of the table ``wom_rule`` with the following fields:

    - id: INTEGER - primary_key - auto increment - arbitrary ID
    - is_input: VARCHAR(255) - the is_input of the rule
    - tool_python_path: VARCHAR(255) - the is_input of the Toolwrapper
    - execution_id: INTEGER - foreign key to the table ``wom_execution`` - the associated execution
    - started_at: INTEGER - unix mtime_epoch_millis [ms] at wich the tool_python_path started its execution
    - finished_at: INTEGER - unix mtime_epoch_millis [ms] at wich the tool_python_path finished its execution
    - mtime_epoch_millis: FLOAT - the total mtime_epoch_millis [ms] tool_python_path execution
    - status: VARCHAR(255) - the final status of the Toolwrapper. it can be:

       - NOT PLANNED: the tool_python_path execution wasn't evene xpected by the user
       - ALREADY EXECUTED: the tool_python_path has been previously executed in an old workflow and doesn't need to be re-executed
       - EXECUTED: the tool_python_path has been executed
       - EXECUTION_ERROR: the tool_python_path has encountered an error during the execution
    """

    __tablename__ = "wom_{}".format(__qualname__)

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255))
    tool_python_path = Column(String(255))
    execution_id = Column(Integer, ForeignKey("wom_Execution.id"))
    started_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)
    run_duration_secs = Column(Integer, nullable=True)
    status = Column(String(255), nullable=True, default="NOT_EXECUTED")

    # One rule has Many table
    tables = relationship("TableInputOutputInformation", back_populates="rule")
    # One rule has Many file
    files = relationship("FileInputOutputInformation", back_populates="rule")
    # One rule has Many option
    options = relationship("Option", back_populates="rule")
    # One rule has one execution
    execution = relationship("Execution", back_populates="rules")

    # parentrules = relationship etc...
    __mapper_args__ = {
        'polymorphic_on': tool_python_path,
        'polymorphic_identity': 'Rule'
    }

    NEW = 1
    READY = 2
    NOT_READY = 3

    def __init__(self, rule_name=""):
        """
        The constructor of the tool_python_path, must not be overwritten.

        self.__state is the state given to the Toolwrapper to let the
        :class:`~.wopmars.framework.management.WorflowManager.WorkflowManager` knows if the Toolwrapper is
        able to be executed or not.
        self.__session is the session (WopmarsSession) associated with the Toolwrapper and which will be used in the run method.
        self.__state is an integer which says the actual state of the TooLWrapper: ``NEW``, ``READY``, ``NOT_READY``

        :param rule_name: the is_input of the rule
        :type rule_name: str
        """
        super().__init__(name=rule_name)
        self.__state = Rule.NEW
        self.__session = None

    ### PARSING METHODS

    def is_content_respected(self):
        """
        Parsing method:

        This method checks if the parameters dictionary are properly formed, according to the specifications of the
        wrapper developer.

        Call of the methods:

        - :meth:`~.wopmars.framework.database.Rule.Rule.is_options_respected`
        - :meth:`~.wopmars.framework.database.Rule.Rule.is_input_respected`
        - :meth:`~.wopmars.framework.database.Rule.Rule.is_output_respected`
        """
        # the options have to be checked first because they can alter the behavior of the is_input_respected and
        # is_output_respected methods
        self.is_options_respected()

        self.is_input_respected()
        self.is_output_respected()

    def is_input_respected(self):
        """
        Parsing method:

        Check if the input file variables names associated with the tool_python_path are ok according to the tool_python_path developer.

        It checks if the input variable names exists or not. If not, throws a WopMarsParsingException.

        This method calls the :meth:`~.wopmars.framework.database.Rule.Rule.specify_input_file` method
        which have been written by the tool_python_path developer.

        :raise WopMarsException: The input are not respected by the user.
        """
        set_input_file_names = set([f_input.name for f_input in self.files if f_input.type.is_input == 1])
        # check if the input file names for the Rule are coherent with the Rule specifications
        if set_input_file_names != set(self.specify_input_file()):
            raise WopMarsException("The content of the definition file is not valid.",
                                   "The given input file variable names for " + self.__class__.__name__ +
                                   " (rule " + str(self.name) + ")" +
                                   " are not correct, they should be: " +
                                   "\n\t'{0}'".format("'\n\t'".join(self.specify_input_file())) +
                                   "\n" + "They are:" +
                                   "\n\t'{0}'".format("'\n\t'".join(set_input_file_names))
                                   )

        set_input_table = set([t_input for t_input in self.tables if t_input.type.is_input == 1])
        set_input_table_names = set([t_input.tablename for t_input in set_input_table])

        # check if the input table names for the Rule are coherent with the Rule specifications
        # this condition may be a duplicate... # todo to fix?
        if set_input_table_names != set(self.specify_input_table()):
            raise WopMarsException("The content of the definition file is not valid.",
                                   "The given input table variable names for " + self.__class__.__name__ +
                                   " (rule " + str(self.name) + ")" +
                                   " are not correct, they should be: " +
                                   "\n\t'{0}'".format("'\n\t'".join(self.specify_input_table())) +
                                   "\n" + "They are:" +
                                   "\n\t'{0}'".format("'\n\t'".join(set_input_table_names))
                                   )

        for t_input in set_input_table:
            s_tablename = t_input.tablename
            if s_tablename not in self.specify_input_table():
                raise WopMarsException("The content of the definition file is not valid.",
                                       "The given input tablenames for " + 
                                       self.__class__.__name__ + " (rule " + str(self.name) + ")" +
                                       " is not correct. it should be in: " +
                                       "\n\t'{0}'".format("'\n\t'".join(self.specify_input_table())) +
                                       "\n" + "It is:" +
                                       "\n\t'" + s_tablename
                                       )
            s_tablename_of_model = t_input.get_table().__tablename__
            if s_tablename_of_model not in self.specify_input_table():
                raise WopMarsException("The content of the definition file is not valid.",
                                       "The given tablename of model for " +
                                       self.__class__.__name__ +
                                       " (rule " + str(self.name) + ")" +
                                       " is not correct. it should be in: " +
                                       "\n\t'{0}'".format("'\n\t'".join(self.specify_input_table())) +
                                       "\n" + "It is:" +
                                       "\n\t'" + s_tablename_of_model
                                       )

    def is_output_respected(self):
        """
        Parsing method:

        Check if the output dictionary given in the constructor is properly formed for the tool.

        It checks if the output variable names exists or not. If not, throws a WopMarsParsingException.

        This method calls the "specify_output_file" method which have been written by the tool_python_path developer.

        :raises WopMarsException: The output are not respected by the user.
        """
        if set([f_output.name for f_output in self.files if f_output.type.is_input == 0]) != set(self.specify_output_file()):
            raise WopMarsException("The content of the definition file is not valid.",
                                   "The given output variable names for " + self.__class__.__name__ +
                                   " (rule " + str(self.name) + ")" +
                                   " are not correct, they should be: " +
                                   "\n\t'{0}'".format("'\n\t'".join(self.specify_output_file())) +
                                   "\n" + "They are:" +
                                   "\n\t'{0}'".format("'\n\t'".join([f.name for f in self.files if f.type.is_input == 0]))
                                   )

        set_output_table = set([t_output for t_output in self.tables if t_output.type.is_input == 0])
        set_output_table_names = set([t_input.tablename for t_input in set_output_table])
        if set_output_table_names != set(self.specify_output_table()):
            raise WopMarsException("The content of the definition file is not valid.",
                                   "The given output table variable names for " + self.__class__.__name__ +
                                   " (rule " + str(self.name) + ")" +
                                   " are not correct, they should be: " +
                                   "\n\t'{0}'".format("'\n\t'".join(self.specify_output_table())) +
                                   "\n" + "They are:" +
                                   "\n\t'{0}'".format("'\n\t'".join(set_output_table_names))
                                   )
        for t_output in set_output_table:
            s_tablename = t_output.tablename
            if s_tablename not in self.specify_output_table():
                raise WopMarsException("The content of the definition file is not valid.",
                                       "The given output tablenames for " + 
                                       self.__class__.__name__ + " (rule " + str(self.name) + ")" +
                                       " is not correct. it should be in: " +
                                       "\n\t'{0}'".format("'\n\t'".join(self.specify_output_table())) +
                                       "\n" + "It is:" +
                                       "\n\t'" + s_tablename
                                       )   

    def is_options_respected(self):
        """
        Parsing method:

        This method check if the params given in the constructor are properly formed for the tool.

        It checks if the params names given by the user exists or not, if the type correspond and if the required
        options are given. If not, throws a WopMarsParsingException.

        This method calls the "specify_params" method of the tool_python_path. This method should return a dictionnary
        associating the is_input of the option with a String containing the types allowed with it. A "|" is used between
        each types allowed for one option.

        Example:

        .. code-block:: python

            {
                'option1': "int",
                'option2': "required|str",
            }

        :raises WopMarsException: If the params names and types are not respected by the user.
        """
        dict_wrapper_opt_carac = self.specify_params()

        # check if the given options are authorized
        if not set([opt.name for opt in self.options]).issubset(dict_wrapper_opt_carac):
            raise WopMarsException("The content of the definition file is not valid.",
                                   "The given option variable for the rule " + str(self.name) + " -> " + self.__class__.__name__ +
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
            if "required" in str(dict_wrapper_opt_carac[opt]).lower() and opt not in [opt2.name for opt2 in self.options]:
                raise WopMarsException("The content of the definition file is not valid.",
                                       "The option '" + opt + "' has not been provided but it is required.")

    def follows(self, other):
        """
        Parsing method:

        Check whether the "self" follows directly "other" in the execution DAG.

        Check whether "other" has one output value in "self" possible input values.
        The output value are given from the Relationnal mapping between toolwrappers and related objects:
        * TableInputOutputInformation
        * FileInputOutputInformation

        :param other: Rule that is possibly a predecessor of "self"
        :return: bool True if "self" follows "other"
        """
        for rule_f_path in [f.path for f in self.files if f.type.is_input == 1]:
            for rule_f2_path in [f.path for f in other.files if f.type.is_input == 0]:
                if rule_f_path == rule_f2_path:
                    return True

        for rule_t_name in [t.model_py_path for t in self.tables if t.type.is_input == 1]:
            for rule_t2_name in [t.model_py_path for t in other.tables if t.type.is_input == 0]:
                if rule_t_name == rule_t2_name:
                    return True

        return False

    ### Workflow Manager methods

    def get_input_files_not_ready(self):
        """
        Check if inputs are ready

        :return: bool - True if inputs are ready.
        """
        input_files_not_ready = []
        input_files = [f for f in self.files if f.type.is_input == 1]
        for i in input_files:
            if not i.is_ready():
                input_files_not_ready.append(i)
        return input_files_not_ready

    def are_inputs_ready(self):
        """
        Check if inputs are ready

        :return: bool - True if inputs are ready.
        """
        input_files = [f for f in self.files if f.type.is_input == 1]
        Logger.instance().debug("Inputs files of " + str(self.__class__.__name__) + ": " + str([i.name for i in input_files]))
        for i in input_files:
            if not i.is_ready():
                Logger.instance().debug("Input: " + str(i.name) + " is not ready.")
                self.__state = Rule.NOT_READY
                return False
            Logger.instance().debug("Input: " + str(i.name) + " is ready.")

        input_tables = [t for t in self.tables if t.type.is_input == 1]
        Logger.instance().debug("Inputs tables of " + str(self.__class__.__name__) + ": " + str([i.tablename for i in input_tables]))
        for i in input_tables:
            if not i.is_ready():
                Logger.instance().debug("Input: " + str(i.tablename) + " is not ready.")
                self.__state = Rule.NOT_READY
                return False
            Logger.instance().debug("Input: " + str(i.tablename) + " is ready.")

        self.__state = Rule.READY
        return True

    def set_args_time_and_size(self, type, dry=False):
        """
        WorkflowManager method:

        The mtime_epoch_millis and the size of the files are set according to the actual mtime_epoch_millis of last modification and size of the system files

        The mtime_epoch_millis of the tables are set according to the mtime_epoch_millis of last modification notified in the modification_table table
        If the type of InputOutput is "output" and the execution is "not dry", the mtime_epoch_millis in modification_table is set to the
        current mtime_epoch_millis.mtime_epoch_millis().

        # todo modify it to take commits into account isntead of the status of 'output' of a table

        :param type: "input" or "output"
        :type type: str
        :param dry: Say if the execution has been simulated.
        :type dry: bool
        """
        session = SQLManager.instance().get_session()
        for f in [f for f in self.files if f.type.is_input == type]:
            try:
                mtime_epoch_millis, mtime_human = get_mtime(f.path)
                f.mtime_human = mtime_human
                f.mtime_epoch_millis = mtime_epoch_millis
                size = os.path.getsize(f.path)
                f.size = size
                size = os.path.getsize(f.path)
            except FileNotFoundError as FE:
                # todo ask lionel sans ce rollback, ca bug, pourquoi? la session est vide... comme si la query etait bloquante
                if not OptionManager.instance()["--dry-run"]:
                    session.rollback()
                    raise WopMarsException("Error during the execution of the workflow",
                                           "The " + type + " file " + str(f.path) + " of rule " + str(self.name) +
                                           " doesn't exist")
                else:
                    # in dry-run mode, input/output files might not exist
                    mtime_epoch_millis = None
                    size = None
            f.used_at = mtime_epoch_millis
            f.size = size
            session.add(f)
            if type == 1:
                Logger.instance().debug("Input file " + str(f) + " used.")
            elif type == 0 and dry:
                Logger.instance().debug("Output file " + str(f) + " has been loaded from previous execution.")
            elif type == 0 and not dry:
                Logger.instance().debug("Output file " + str(f) + " has been created.")
        # this commit is due to a bug that i couldn't figure out: the session empty itself between the two loops...
        # this is not good at all since it may lead to inconsistence in the database
        session.commit()

        for t in [t for t in self.tables if t.type.is_input == type]:
            t.mtime_human = t.modification.mtime_human
            t.mtime_epoch_millis = t.modification.mtime_epoch_millis
            # t.used_at = t.modification.mtime_epoch_millis
            session.add(t)
        session.commit()

    def same_input_than(self, other):
        """
        Never used.

        Check if the other Rule have the same input than self.

        The input are say "the same" if:
            - The table have the same is_input and the same last modification mtime_epoch_millis
            - The file have the same is_input, the same lastm modification mtime_epoch_millis and the same size

        :param other: an other Toolwrapper which maybe as the same inputs
        :type other: :class:`~.wopmars.framework.database.tables.Rule.Rule`

        :return: bool
        """
        for t in [t for t in self.tables if t.type.is_input == 1]:
            is_same = False
            for t2 in [t2 for t2 in other.tables if t2.type.is_input == 1]:
                # two tables are the same if they have the same model/tablename/modification mtime_epoch_millis
                if (t.model_py_path == t2.model_py_path and
                    t.tablename == t2.tablename and
                       t.used_at == t2.used_at):
                    is_same = True
                    break
            if not is_same:
                return False

        for f in [f for f in self.files if f.type.is_input == 1]:
            is_same = False
            for f2 in [f2 for f2 in other.files if f2.type.is_input == 1]:
                # two files are the same if they have the same is_input, path, size and modification mtime_epoch_millis
                if (f.name == f2.name and
                        f.path == f2.path and
                        f.used_at == f2.used_at and
                        f.size == f2.size):
                    is_same = True
                    break
            if not is_same:
                return False
        return True

    def is_output_more_recent_than_input(self):
        """
        Check for files and tables if the outputs are more recent than inputs.

        In a conventionnal use of WoPMaRS, the output are supposed to be younger than the inputs. If they are not,
        we can consider that the input has changed since the last execution and the output has to be re-written.

        :return: Bool: True if the output is actually more recent than input
        """
        most_recent_input = max([get_mtime(f.path)[0] for f in self.files if f.type.is_input == 1]
                                + [t.modification.mtime_epoch_millis for t in self.tables if t.type.is_input == 1])
        oldest_output = min([get_mtime(f.path)[0] for f in self.files if f.type.is_input == 0]
                            + [t.modification.mtime_epoch_millis for t in self.tables if t.type.is_input == 0])
        # in seconds since the begining of mtime_epoch_millis (computer), the oldest thing has a lower number of seconds
        return most_recent_input < oldest_output

    def same_output_than(self, other):
        """
        Never used.

        Check if the output of self is the same than other.

        Checks only if the file names, table names and models are the same.

        :return: bool
        """
        for t in [t for t in self.tables if t.type.is_input == 0]:
            is_same = False
            for t2 in [t2 for t2 in other.tables if t2.type.is_input == 0]:
                if t.model_py_path == t2.model_py_path and t.tablename == t2.tablename:
                    is_same = True
                    break
            if not is_same:
                return False

        for f in [f for f in self.files if f.type.is_input == 1]:
            is_same = False
            for f2 in [f2 for f2 in other.files if f2.type.is_input == 1]:
                if (f.name == f2.name and
                        f.path == f2.path):
                    is_same = True
                    break
            if not is_same:
                return False
        return True

    def does_output_exist(self):
        """
        Check if the output of the Rule exists.

        For files, it means that the file exists on the system.
        For tables, it means that the table is not empty.

        :return: Bool: True if outputs exist.
        """
        for of in [f for f in self.files if f.type.is_input == 0]:
            if not os.path.exists(of.path):
                return False

        for ot in [t for t in self.tables if t.type.is_input == 0]:
            if not SQLManager.instance().get_session().query(ot.get_table()).count():
                return False
        return True

    def get_state(self):
        return self.__state

    def set_execution_infos(self, start=None, stop=None, status=None):
        """
        Generic method to set the informations relatives to the execution of the Rule.

        :param start: The mtime_epoch_millis of start of the Toolwrapper
        :param stop: The mtime_epoch_millis of end of the Toolwrapper
        :param status: The status of the Toolwrapper
        """
        if start is not None:
            self.started_at = start
        if stop is not None:
            self.finished_at = stop
        if self.started_at is not None and self.finished_at is not None:
            self.run_duration_secs = (self.finished_at - self.started_at).total_seconds()
        if status is not None:
            self.status = status

    def set_session(self, session):
        self.__session = session

    def __eq__(self, other):
        """
        Two ToolWrapper objects are equals if all their attributes are equals.

        We check if the files, tables and options are the same.
        :param other: ToolWrapper
        :type other: Rule
        :return: Bool: True if the ToolWrappers are equals.
        """
        return (isinstance(other, self.__class__) and
                self.same_files(other, True) and
                self.same_tables(other, True) and
                self.same_files(other, False) and
                self.same_tables(other, False) and
                self.same_options(other))

    def same_files(self, other, is_name):
        """
        Check if the files of a ToolWrapper are the same than the files of the other for a given type (input or output).

        :param other: ToolWrapper with which you need to compare
        :type other: Rule
        :param is_name: The is_input of the type of file (input or output)
        :type is_name: str
        :return: Bool: True if the files are the same
        """
        for f in [rf for rf in self.files if rf.type.is_input == is_name]:
            is_in = bool([rf for rf in other.files if (os.path.abspath(f.path) == os.path.abspath(rf.path) and
                                                       f.name == rf.name and
                                                       rf.type.is_input == is_name)])
            if not is_in:
                return False
        return True

    def same_tables(self, other, is_input):
        """
        Check if the tables of a ToolWrapper are the same than the tables of the other for a given type (input or output).

        :param other: ToolWrapper with which you need to compare
        :type other: Rule
        :param is_input: The is_input of the type of table (input or output)
        :type is_input: str
        :return: Bool: True if the tables are the same
        """
        for t in [t for t in self.tables if t.type.is_input == is_input]:
            is_in = bool([t for t in other.tables if (t.model_py_path == t.model_py_path and
                                                      t.type.is_input == is_input and
                                                      t.tablename == t.tablename)])
            if not is_in:
                return False
        return True

    def same_options(self, other):
        """
        Check if the options of a ToolWrapper are the same the options of the other.

        :param other: ToolWrapper with which you need to compare.
        :type other: Rule
        :return: Bool: True if the options are the same.
        """
        for opt in self.options:
            is_in = bool([o for o in other.options if (o.name == opt.name and
                                                       o.value == opt.value)])

            if not is_in:
                return False
        return True

    def __hash__(self):
        """
        Redefining the hash method allows Rule objects to be indexed in sets and dict.

        Needed to use Rule as nodes of the DiGraph.

        :return: int
        """
        return id(self)

    def __repr__(self):
        """
        Return the string representing the tool_python_path in the DAG.

        :return: String representing the tool_python_path
        """
        s = "\""
        s += "Rule " + self.name
        s += "\\n"
        s += "tool: " + self.__class__.__name__
        s += "\\n"
        for input_f in [f for f in self.files if f.type.is_input == 1]:
            s += "\\n\t\t" + input_f.name + ": " + str(input_f.path)
        for input_t in [t for t in self.tables if t.type.is_input == 1]:
            s += "\\n\t\tinput_table: " + input_t.name
        s += "\\n"
        for output_f in [f for f in self.files if f.type.is_input == 0]:
            s += "\\n\t\t" + output_f.name + ": " + str(output_f.path)
        for output_t in [t for t in self.tables if t.type.is_input == 0]:
            s += "\\n\t\toutput_table: " + output_t.name
        s += "\""
        return s

    def dot_label(self):
        """Label for the dot dag"""
        inputs_list_str = [str(i).replace(":", "") for i in self.files + self.tables if i.type.is_input == 1]
        outputs_list_str = [str(o).replace(":", "") for o in self.files + self.tables if o.type.is_input == 0]
        params_list_str = [str(p).replace(":","") for p in self.options]
        s = ""
        s += "Rule " + self.name + "\n"
        s += "Rule " + self.__class__.__name__ + "\n"
        s += "Inputs\n" + "\n\t".join(inputs_list_str) + "\n"
        s += "Outputs\n" + "\n".join(outputs_list_str) + "\n"
        s += "Parameters\n" + "\n".join(params_list_str) + "\n"
        return(s)

    def __str__(self):
        inputs_list_str = [str(i) for i in self.files + self.tables if i.type.is_input == 1]
        outputs_list_str = [str(o) for o in self.files + self.tables if o.type.is_input == 0]
        params_list_str = [str(p) for p in self.options]
        s = ""
        s += "Rule " + str(self.name) + ":" + "\n"
        s += "\ttool: " + str(self.tool_python_path) + "\n"
        if len(inputs_list_str) > 0:
            s += "\tinput:" + "\n"
            s += "\t\t" + "\n\t\t".join(inputs_list_str)
            s += "\n"
        if len(outputs_list_str) > 0:
            s += "\toutput:" + "\n"
            s += "\t\t" + "\n\t\t".join(outputs_list_str)
            s += "\n"
        if len(params_list_str) > 0:
            s += "\tparams:" + "\n"
            s += "\t\t" + "\n\t\t".join(params_list_str)
        return s

    # ###### Method that worker developper should implement#######

    def specify_input_file(self):
        """
        Should be implemented by the tool_python_path developper.

        This method return a List of string containing the input file variable names as String.
        :return: [String]
        """
        return []

    def specify_input_table(self):
        """
        Should be implemented by the tool_python_path developper.

        This method return a List of string containing the input table names names as String.
        :return: [String]
        """
        return []

    def specify_output_file(self):
        """
        Should be implemented by the tool_python_path developper.

        This method return a List of string containing the output file variable names as String.
        :return: [String]
        """
        return []

    def specify_output_table(self):
        """
        Should be implemented by the tool_python_path developper.

        This method return a List of string containing the output table names as String.
        :return: [String]
        """
        return []

    def specify_params(self):
        """
        Should be implemented by the tool_python_path developper.

        This method return a dict of string associated with string. Keys are the is_input of the options and values, their types.

        :return: {String: String}
        """
        return {}

    def run(self):
        """
        Should be implemented by the tool_python_path developper.

        The core function of the Rule is this method. It wraps the actual execution of the tool underlying the Rule.

        :raises NotImplementedError: If it doesn't have been implemented by the Rule Developer.
        """
        raise NotImplementedError("The method run of the Rule " + str(self.tool_python_path) + " should be implemented")

    ### Methods availables for the tool developer

    def input_file(self, key):
        """
        Return the path of the specified input file.

        :param key: String the is_input of the variable containing the path
        :return:
        """
        try:
            return [f.path for f in self.files if f.name == key and f.type.is_input == 1][0]
        except IndexError:
            raise WopMarsException("Error during the execution of the Rule " + str(self.tool_python_path) +
                                   " (rule " + self.name + ").",
                                   "The input file " + str(key) + " has not been specified.")

    def input_table(self, key):
        """
        Return the input table object of the given is_input.

        :param key: String: the is_input of the Table object.
        :return:
        """
        try:
            return [t for t in self.tables if t.tablename == key and t.type.is_input == 1][0].get_table()
        except IndexError:
            raise WopMarsException("Error during the execution of the Rule " + str(self.tool_python_path) +
                                   " (rule " + self.name + ").",
                                   "The input table " + str(key) + " has not been specified.")

    def output_file(self, key):
        """
        Return the path of the specified output file.

        :param key: String the is_input of the variable containing the path
        :return:
        """
        try:
            return [f.path for f in self.files if f.name == key and f.type.is_input == 0][0]
        except IndexError:
            raise WopMarsException("Error during the execution of the Rule " + str(self.tool_python_path) +
                                   " (rule " + self.name + ").",
                                   "The output file " + str(key) + " has not been specified.")

    def output_table(self, key):
        """
        Return the output table object of the given is_input.

        :param key: String: the is_input of the Table object.
        :return:
        """
        try:
            return [t for t in self.tables if t.tablename == key and t.type.is_input == 0][0].get_table()
        except IndexError:
            raise WopMarsException("Error during the execution of the Rule " + str(self.tool_python_path) +
                                   " (rule " + self.name + ").",
                                   "The output table " + str(key) + " has not been specified.")

    def option(self, key):
        """
        Return the value associated with the key option.

        If no value is associated with key, return None.

        :param key: The is_input of the option
        :type key: str
        :return:
        """
        try:
            value = [o.value for o in self.options if o.name == key][0]
            list_splitted_carac = self.specify_params()[key].split("|")
            for s_type in list_splitted_carac:
                s_formated_type = s_type.strip().lower()
                # check if the carac is a castable type
                if s_formated_type in Option.static_option_castable:
                    value = eval(s_formated_type)(value)
                    break
            return value
        except IndexError as e:
            # antipattern, this is bad, but I deleted the warning because if the Rule Developer put his call to
            # option in a loop, there will be too mutch output
            pass
            return None

    def session(self):
        return self.__session

    def log(self, level, msg):
        """
        use by the tool_python_path developer in order to have a dedicated logger.

        :param level: The level of logging you need: "debug", "info", "warning", "error"
        :type level: str
        :param msg: The actual string to log.
        :type msg: str
        """
        if level == "debug":
            Logger.instance().toolwrapper_debug(msg, self.tool_python_path)
        elif level == "info":
            Logger.instance().toolwrapper_info(msg, self.tool_python_path)
        elif level == "warning":
            Logger.instance().toolwrapper_debug(msg, self.tool_python_path)
        elif level == "error":
            Logger.instance().toolwrapper_error(msg, self.tool_python_path)
        else:
            raise WopMarsException("Error in the Toolwrapper definition of method run()",
                                   "The is no logging level associated with " + str(level) + ". " +
                                   "The authorized ones are: debug, info, warning, error")
