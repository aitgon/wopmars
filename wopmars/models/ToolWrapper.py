import os
import pathlib

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from wopmars.Base import Base
from wopmars.SQLManager import SQLManager
from wopmars.models.Option import Option
from wopmars.utils.Logger import Logger
from wopmars.utils.OptionManager import OptionManager
from wopmars.utils.WopMarsException import WopMarsException
from wopmars.utils.various import get_mtime, get_current_time
from wopmars.models.TableModificationTime import TableModificationTime


class ToolWrapper(Base):
    """
    The class ToolWrapper is the superclass of the wrappers which will be designed by the wrapper developers. It is the
    SQLAlchemy Model of the table ``wom_rule`` with the following fields:

    - id: INTEGER - primary_key - auto increment - arbitrary ID
    - rule_name: VARCHAR(255) - the name of the rule
    - tool_python_path: VARCHAR(255) - the is_input of the Toolwrapper
    - execution_id: INTEGER - foreign key to the table ``wom_execution`` - the associated execution
    - started_at: INTEGER - unix mtime_epoch_millis [ms] at wich the tool_python_path started its execution
    - finished_at: INTEGER - unix mtime_epoch_millis [ms] at wich the tool_python_path finished its execution
    - mtime_epoch_millis: FLOAT - the total mtime_epoch_millis [ms] tool_python_path execution
    - status: VARCHAR(255) - the final status of the Toolwrapper. it can be:

       - NOT PLANNED: the tool_python_path execution was not even expected by the user
       - ALREADY EXECUTED: the tool_python_path has been previously executed in an old workflow and does not need to be re-executed
       - EXECUTED: the tool_python_path has been executed
       - ERROR: the tool_python_path has encountered an error during the execution
    """

    __tablename__ = "wom_{}".format(__qualname__)

    id = Column(Integer, primary_key=True, autoincrement=True)
    rule_name = Column(String(255))
    tool_python_path = Column(String(255))
    execution_id = Column(Integer, ForeignKey("wom_Execution.id"))
    started_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)
    run_duration_secs = Column(Integer, nullable=True)
    status = Column(String(255), nullable=True, default="NOT_EXECUTED")

    # One rule has many tables
    relation_toolwrapper_to_tableioinfo = relationship("TableInputOutputInformation", back_populates="relation_file_or_tableioinfo_to_toolwrapper", cascade="all, delete, delete-orphan")
    # One rule has many files
    relation_toolwrapper_to_fileioinfo = relationship("FileInputOutputInformation", back_populates="relation_file_or_tableioinfo_to_toolwrapper", cascade="all, delete, delete-orphan")
    # One option is used by many toolwrappers
    relation_toolwrapper_to_option = relationship("Option", back_populates="relation_option_to_toolwrapper", cascade="all, delete, delete-orphan")
    # One rule has one execution
    # execution = relationship("Execution", back_populates="rules")
    relation_toolwrapper_to_execution = relationship("Execution", back_populates="relation_execution_to_toolwrapper")

    # parentrules = relationship etc...
    __mapper_args__ = {
        'polymorphic_on': tool_python_path,
        'polymorphic_identity': 'ToolWrapper'
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
        self.session is the session (WopmarsSession) associated with the Toolwrapper and which will be used in the run method.
        self.__state is an integer which says the actual state of the TooLWrapper: ``NEW``, ``READY``, ``NOT_READY``

        :param rule_name: the is_input of the rule
        :type rule_name: str
        """
        super().__init__(rule_name=rule_name)
        self.__state = ToolWrapper.NEW
        self.session = None

    def is_content_respected(self):
        """
        Parsing method:

        This method checks if the parameters dictionary are properly formed, according to the specifications of the
        wrapper developer.

        Call of the methods:

        - :meth:`~.wopmars.framework.database.ToolWrapper.ToolWrapper.is_options_respected`
        - :meth:`~.wopmars.framework.database.ToolWrapper.ToolWrapper.is_input_or_output_respected`
        - :meth:`~.wopmars.framework.database.ToolWrapper.ToolWrapper.is_output_respected`
        """
        # the relation_toolwrapper_to_option have to be checked first because they can alter the behavior of the is_input_or_output_respected and
        # is_output_respected methods
        self.is_options_respected()

        # Check whether input is respected
        self.is_input_or_output_respected(is_input=True)
        # Check whether output is respected
        self.is_input_or_output_respected(is_input=False)

    def is_input_or_output_respected(self, is_input):
        """
        Parsing method:

        Check if the input (is_input=1) or output (is_input=0) file and table variables names associated with the
        tool_wrapper are respected. If not, throws a WopMarsParsingException.

        This method calls the :meth:`~.wopmars.framework.database.ToolWrapper.ToolWrapper.specify_input_file` method
        which have been written by the tool_python_path developer.

        :raise WopMarsException: The input are not respected by the user.
        """

        fileioinfo_name_set = set([fileioinfo.file_key for fileioinfo in self.relation_toolwrapper_to_fileioinfo
                                    if fileioinfo.relation_file_or_tableioinfo_to_typeio.is_input == is_input])

        tableio_tablename_set = set([tableioinfo.table_key for tableioinfo in self.relation_toolwrapper_to_tableioinfo
                                     if tableioinfo.relation_file_or_tableioinfo_to_typeio.is_input == is_input])

        # tableio_tablename_set = set([tableioinfo.model_py_path.split('.')[-1] for tableioinfo in self.relation_toolwrapper_to_tableioinfo
        #                              if tableioinfo.relation_file_or_tableioinfo_to_typeio.is_input == is_input])

        if is_input:

            ############################################################################################################
            #
            # Input files
            #
            ############################################################################################################

            tool_wrapper_specified_files = self.specify_input_file()

            if fileioinfo_name_set != set(tool_wrapper_specified_files):
                msg_err = "The given input file variable names for {} (rule {}) are not correct." \
                          " They should be: {}" \
                          " They are: {}"\
                    .format(self.__class__.__name__, str(self.rule_name), "'\n\t'".join(tool_wrapper_specified_files),
                            "'\n\t'".join(fileioinfo_name_set))
                raise WopMarsException(msg_err)

            ############################################################################################################
            #
            # Input tables
            #
            ############################################################################################################

            tool_wrapper_specified_tables = self.specify_input_table()

            if tableio_tablename_set != set(tool_wrapper_specified_tables):
                msg_err = "The given input file variable names for {} (rule {}) are not correct." \
                          " They should be: {}" \
                          " They are: {}"\
                    .format(self.__class__.__name__, str(self.rule_name), "'\n\t'".join(tool_wrapper_specified_tables),
                            "'\n\t'".join(tableio_tablename_set))
                raise WopMarsException(msg_err)

        else:

            ############################################################################################################
            #
            # Output files
            #
            ############################################################################################################

            tool_wrapper_specified_files = self.specify_output_file()

            if fileioinfo_name_set != set(tool_wrapper_specified_files):
                msg_err = "The given output file variable names for {} (rule {}) are not correct." \
                          " They should be: {}" \
                          " They are: {}"\
                    .format(self.__class__.__name__, str(self.rule_name), "'\n\t'".join(tool_wrapper_specified_files),
                            "'\n\t'".join(fileioinfo_name_set))
                raise WopMarsException(msg_err)

            ############################################################################################################
            #
            # Output tables
            #
            ############################################################################################################

            tool_wrapper_specified_tables = self.specify_output_table()

            if tableio_tablename_set != set(tool_wrapper_specified_tables):
                msg_err = "The given output table variable names for {} (rule {}) are not correct." \
                          " They should be: {}" \
                          " They are: {}"\
                    .format(self.__class__.__name__, str(self.rule_name), "'\n\t'".join(tool_wrapper_specified_tables),
                            "'\n\t'".join(tableio_tablename_set))
                raise WopMarsException(msg_err)

    def is_options_respected(self):
        """
        Parsing method:

        This method check if the params given in the constructor are properly formed for the tool.

        It checks if the params names given by the user exists or not, if the type correspond and if the required
        relation_toolwrapper_to_option are given. If not, throws a WopMarsParsingException.

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

        # check if the given relation_toolwrapper_to_option are authorized
        if not set([opt.name for opt in self.relation_toolwrapper_to_option]).issubset(dict_wrapper_opt_carac):
            raise WopMarsException("The content of the definition file is not valid.",
                                   "The given option variable for the rule " + str(self.rule_name) + " -> " + self.__class__.__name__ +
                                   " are not correct, they should be in: " +
                                   "\n\t'{0}'".format("'\n\t'".join(dict_wrapper_opt_carac)) +
                                   "\n" + "They are:" +
                                   "\n\t'{0}'".format("'\n\t'".join([opt.name for opt in self.relation_toolwrapper_to_option]))
                                   )

        # check if the types correspond
        for opt in self.relation_toolwrapper_to_option:
            opt.correspond(dict_wrapper_opt_carac[opt.name])

        # check if the required relation_toolwrapper_to_option are given
        for opt in dict_wrapper_opt_carac:
            if "required" in str(dict_wrapper_opt_carac[opt]).lower() and opt not in [opt2.name for opt2 in self.relation_toolwrapper_to_option]:
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

        :param other: ToolWrapper that is possibly a predecessor of "self"
        :return: bool True if "self" follows "other"
        """
        for rule_f_path in [f.path for f in self.relation_toolwrapper_to_fileioinfo if f.relation_file_or_tableioinfo_to_typeio.is_input == 1]:
            for rule_f2_path in [f.path for f in other.relation_toolwrapper_to_fileioinfo if f.relation_file_or_tableioinfo_to_typeio.is_input == 0]:
                if rule_f_path == rule_f2_path:
                    return True

        for rule_t_name in [t.model_py_path for t in self.relation_toolwrapper_to_tableioinfo if t.relation_file_or_tableioinfo_to_typeio.is_input == 1]:
            for rule_t2_name in [t.model_py_path for t in other.relation_toolwrapper_to_tableioinfo if t.relation_file_or_tableioinfo_to_typeio.is_input == 0]:
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
        input_files = [f for f in self.relation_toolwrapper_to_fileioinfo if f.relation_file_or_tableioinfo_to_typeio.is_input == 1]
        for i in input_files:
            if not i.is_ready():
                input_files_not_ready.append(i)
        return input_files_not_ready

    def are_inputs_ready(self):
        """
        Check if inputs are ready

        :return: bool - True if inputs are ready.
        """
        input_files = [f for f in self.relation_toolwrapper_to_fileioinfo if f.relation_file_or_tableioinfo_to_typeio.is_input == 1]
        Logger.instance().debug("Inputs files of " + str(self.__class__.__name__) + ": " + str([i.file_key for i in input_files]))
        for i in input_files:
            if not i.is_ready():
                Logger.instance().debug("Input: " + str(i.file_key) + " is not ready.")
                self.__state = ToolWrapper.NOT_READY
                return False
            Logger.instance().debug("Input: " + str(i.file_key) + " is ready.")

        input_tables = [t for t in self.relation_toolwrapper_to_tableioinfo if t.relation_file_or_tableioinfo_to_typeio.is_input == 1]
        Logger.instance().debug("Inputs tables of " + str(self.__class__.__name__) + ": " + str([i.table_key for i in input_tables]))
        for i in input_tables:
            if not i.is_ready():
                Logger.instance().debug("Input: " + str(i.table_key) + " is not ready.")
                self.__state = ToolWrapper.NOT_READY
                return False
            Logger.instance().debug("Input: " + str(i.table_key) + " is ready.")

        self.__state = ToolWrapper.READY
        return True

    def set_args_time_and_size(self, is_input, dry=False):
        """
        WorkflowManager method:

        The mtime_epoch_millis and the size of the files are set according to the actual mtime_epoch_millis of last modification and size of the system files

        The mtime_epoch_millis of the tables are set according to the mtime_epoch_millis of last modification notified in the modification_table table
        If the is_input of InputOutput is "output" and the execution is "not dry", the mtime_epoch_millis in modification_table is set to the
        current mtime_epoch_millis.mtime_epoch_millis().

        # totodo LucG modify it to take commits into account instead of the status of 'output' of a table

        :param is_input: "input" or "output"
        :is_input is_input: bool
        :param dry: Say if the execution has been simulated.
        :is_input dry: bool
        """
        session = SQLManager.instance().get_session()
        for f in [f for f in self.relation_toolwrapper_to_fileioinfo if f.relation_file_or_tableioinfo_to_typeio.is_input == is_input]:
            try:
                mtime_epoch_millis, mtime_human = get_mtime(f.path)
                f.mtime_human = mtime_human
                f.mtime_epoch_millis = mtime_epoch_millis
                size = os.path.getsize(f.path)
                f.size = size
                size = os.path.getsize(f.path)
            except FileNotFoundError as FE:
                # totodo LucG ask lionel sans ce rollback, ca bug, pourquoi? la session est vide... comme si la query etait bloquante
                if not OptionManager.instance()["--dry-run"]:
                    session.rollback()
                    raise WopMarsException("Error during the execution of the workflow",
                                           "The " + is_input + " file " + str(f.path) + " of rule " + str(self.rule_name) +
                                           " doesn't exist")
                else:
                    # in dry-run mode, input/output files might not exist
                    mtime_epoch_millis = None
                    size = None
            f.used_at = mtime_epoch_millis
            f.size = size
            session.add(f)
            if is_input == 1:
                Logger.instance().debug("Input file " + str(f) + " used.")
            elif is_input == 0 and dry:
                Logger.instance().debug("Output file " + str(f) + " has been loaded from previous execution.")
            elif is_input == 0 and not dry:
                Logger.instance().debug("Output file " + str(f) + " has been created.")
        # this commit is due to a bug that i couldn't figure out: the session empty itself between the two loops...
        # this is not good at all since it may lead to inconsistence in the database
        session.commit()

        for t in [tableioinfo for tableioinfo in self.relation_toolwrapper_to_tableioinfo
                  if tableioinfo.relation_file_or_tableioinfo_to_typeio.is_input == is_input]:
            t.mtime_human = t.relation_tableioinfo_to_tablemodiftime.mtime_human
            t.mtime_epoch_millis = t.relation_tableioinfo_to_tablemodiftime.mtime_epoch_millis
            # t.used_at = t.relation_tableioinfo_to_tablemodiftime.mtime_epoch_millis
            session.add(t)
        session.commit()

    def same_input_than(self, other):
        """
        Never used.

        Check if the other ToolWrapper have the same inputs than self.

        The input are say "the same" if:
            - The table have the same is_input and the same last modification mtime_epoch_millis
            - The file have the same is_input, the same last modification mtime_epoch_millis and the same size

        :param other: an other Toolwrapper which maybe as the same inputs
        :type other: :class:`~.wopmars.framework.database.relation_toolwrapper_to_tableioinfo.ToolWrapper.ToolWrapper`

        :return: bool
        """

        #############################################################
        #
        # Check file input
        #
        #############################################################

        for f in [f for f in self.relation_toolwrapper_to_fileioinfo if f.relation_file_or_tableioinfo_to_typeio.is_input == 1]:
            is_same = False
            for f2 in [f2 for f2 in other.relation_toolwrapper_to_fileioinfo if f2.relation_file_or_tableioinfo_to_typeio.is_input == 1]:
                # two files are the same if they have the same is_input, path, size and modification mtime_epoch_millis
                if (f.file_key == f2.file_key and f.path == f2.path and
                        f.mtime_epoch_millis == f2.mtime_epoch_millis and f.size == f2.size):
                    is_same = True
                    break
            if not is_same:
                return False

        #############################################################
        #
        # Check table input
        #
        #############################################################

        for t in [t for t in self.relation_toolwrapper_to_tableioinfo if t.relation_file_or_tableioinfo_to_typeio.is_input == 1]:
            is_same = False
            for t2 in [t2 for t2 in other.relation_toolwrapper_to_tableioinfo if t2.relation_file_or_tableioinfo_to_typeio.is_input == 1]:
                # two tables are the same if they have the same model/table_key/modification mtime_epoch_millis
                if (t.model_py_path == t2.model_py_path and t.table_key == t2.table_key and
                       t.mtime_epoch_millis == t2.mtime_epoch_millis):
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

        newest_input_file = [get_mtime(input_fileioinfo.path)[0]
                             for input_fileioinfo in self.relation_toolwrapper_to_fileioinfo
                                  if input_fileioinfo.relation_file_or_tableioinfo_to_typeio.is_input == 1]
        newest_input_table = [input_tableioinfo.relation_tableioinfo_to_tablemodiftime.mtime_epoch_millis
                                   for input_tableioinfo in self.relation_toolwrapper_to_tableioinfo
                                   if input_tableioinfo.relation_file_or_tableioinfo_to_typeio.is_input == 1]
        # newest is supposed to have largest epoch time
        newest_input = max(newest_input_file + newest_input_table)

        oldest_output_file = [get_mtime(output_fileioinfo.path)[0]
                              for output_fileioinfo in self.relation_toolwrapper_to_fileioinfo
                              if output_fileioinfo.relation_file_or_tableioinfo_to_typeio.is_input == 0]
        oldest_output_table = [output_tableioinfo.relation_tableioinfo_to_tablemodiftime.mtime_epoch_millis
                               for output_tableioinfo in self.relation_toolwrapper_to_tableioinfo
                               if output_tableioinfo.relation_file_or_tableioinfo_to_typeio.is_input == 0]
        # newest is supposed to have smallest epoch time
        oldest_output = min(oldest_output_file + oldest_output_table)

        return newest_input < oldest_output

    def same_output_than(self, other):
        """
        Never used.

        Check if the output of self is the same than other.

        Checks only if the file names, table names and models are the same.

        :return: bool
        """
        for t in [t for t in self.relation_toolwrapper_to_tableioinfo if t.relation_file_or_tableioinfo_to_typeio.is_input == 0]:
            is_same = False
            for t2 in [t2 for t2 in other.relation_toolwrapper_to_tableioinfo if t2.relation_file_or_tableioinfo_to_typeio.is_input == 0]:
                if t.model_py_path == t2.model_py_path and t.table_key == t2.table_key:
                    is_same = True
                    break
            if not is_same:
                return False

        for f in [f for f in self.relation_toolwrapper_to_fileioinfo if f.relation_file_or_tableioinfo_to_typeio.is_input == 1]:
            is_same = False
            for f2 in [f2 for f2 in other.relation_typeio_to_fileioinfo if f2.relation_file_or_tableioinfo_to_typeio.is_input == 1]:
                if (f.file_key == f2.file_key and
                        f.path == f2.path):
                    is_same = True
                    break
            if not is_same:
                return False
        return True

    def output_file_exists(self):
        """
        Check if the file exists in the system.

        :return: Bool: True if outputs exist.
        """
        for output_file in [this_file for this_file in self.relation_toolwrapper_to_fileioinfo
                            if this_file.relation_file_or_tableioinfo_to_typeio.is_input == 0]:
            if not os.path.exists(output_file.path):
                return False
        return True

    def output_table_exists(self):
        """
        Check if the table is not empty.

        :return: Bool: True if outputs exist.
        """

        for output_table in [table for table in self.relation_toolwrapper_to_tableioinfo
                             if table.relation_file_or_tableioinfo_to_typeio.is_input == 0]:
            if not SQLManager.instance().get_session().query(output_table.get_table()).count():
                return False
        return True

    def get_state(self):
        return self.__state

    def set_execution_infos(self, start=None, stop=None, status=None):
        """
        Generic method to set the informations relatives to the execution of the ToolWrapper.

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

    def __eq__(self, other):
        """
        Two tool_wrappers are equal for these conditions:

        - Both belong to the same class
        - Both have the same input and output fields

        We check if the files, tables and relation_toolwrapper_to_option are the same.
        :param other: ToolWrapper
        :type other: ToolWrapper
        :return: Bool: True if the ToolWrappers are equals.
        """
        return (isinstance(other, self.__class__) and
                self.same_files(other, is_input=True) and
                self.same_tables(other, is_input=True) and
                self.same_files(other, is_input=False) and
                self.same_tables(other, is_input=False) and
                self.same_options(other))

    def same_files(self, other, is_input):
        """
        Check if the files of a ToolWrapper are the same than the files of the other for a given type (input or output).

        :param other: ToolWrapper with which you need to compare
        :type other: ToolWrapper
        :param is_input: The is_input of the type of file (input or output)
        :type is_input: str
        :return: Bool: True if the files are the same
        """
        for f in [rf for rf in self.relation_toolwrapper_to_fileioinfo if rf.relation_file_or_tableioinfo_to_typeio.is_input == is_input]:
            is_in = bool([rf for rf in other.relation_toolwrapper_to_fileioinfo if (
                    os.path.abspath(f.path) == os.path.abspath(rf.path) and # same absolute path
                    f.file_key == rf.file_key and  # same file field name
                    rf.relation_file_or_tableioinfo_to_typeio.is_input == is_input  # files are same input
            )])
            if not is_in:
                return False
        return True

    def same_tables(self, other, is_input):
        """
        Check if the tables of a ToolWrapper are the same than the tables of the other for a given type (input or output).

        :param other: ToolWrapper with which you need to compare
        :type other: ToolWrapper
        :param is_input: The is_input of the type of table (input or output)
        :type is_input: str
        :return: Bool: True if the tables are the same
        """
        for t in [t for t in self.relation_toolwrapper_to_tableioinfo if t.relation_file_or_tableioinfo_to_typeio.is_input == is_input]:
            is_in = bool([t for t in other.relation_toolwrapper_to_tableioinfo if (t.model_py_path == t.model_py_path and
                                                                                   t.relation_file_or_tableioinfo_to_typeio.is_input == is_input and
                                                                                   t.table_key == t.table_key)])
            if not is_in:
                return False
        return True

    def same_options(self, other):
        """
        Check if the relation_toolwrapper_to_option of a ToolWrapper are the same the relation_toolwrapper_to_option of the other.

        :param other: ToolWrapper with which you need to compare.
        :type other: ToolWrapper
        :return: Bool: True if the relation_toolwrapper_to_option are the same.
        """
        for opt in self.relation_toolwrapper_to_option:
            is_in = bool([o for o in other.relation_toolwrapper_to_option if (o.name == opt.name and
                                                       o.value == opt.value)])

            if not is_in:
                return False
        return True

    def __hash__(self):
        """
        Redefining the hash method allows ToolWrapper objects to be indexed in sets and dict.

        Needed to use ToolWrapper as nodes of the DiGraph.

        :return: int
        """
        return id(self)

    def __repr__(self):
        """
        Return the string representing the tool_python_path in the DAG.

        :return: String representing the tool_python_path
        """
        s = "\""
        s += "ToolWrapper " + self.rule_name
        s += "\\n"
        s += "tool: " + self.__class__.__name__
        s += "\\n"
        for input_f in [f for f in self.relation_toolwrapper_to_fileioinfo if f.relation_file_or_tableioinfo_to_typeio.is_input == 1]:
            s += "\\n\t\t" + input_f.file_key + ": " + str(input_f.path)
        for input_t in [t for t in self.relation_toolwrapper_to_tableioinfo if t.relation_file_or_tableioinfo_to_typeio.is_input == 1]:
            s += "\\n\t\tinput_table: " + input_t.table_key
        s += "\\n"
        for output_f in [f for f in self.relation_toolwrapper_to_fileioinfo if f.relation_file_or_tableioinfo_to_typeio.is_input == 0]:
            s += "\\n\t\t" + output_f.file_key + ": " + str(output_f.path)
        for output_t in [t for t in self.relation_toolwrapper_to_tableioinfo if t.relation_file_or_tableioinfo_to_typeio.is_input == 0]:
            s += "\\n\t\toutput_table: " + output_t.table_key
        s += "\""
        return s

    def dot_label(self):
        """Label for the dot dag"""
        inputs_list_str = [str(i).replace(":", "") for i in self.relation_toolwrapper_to_fileioinfo + self.relation_toolwrapper_to_tableioinfo if i.relation_file_or_tableioinfo_to_typeio.is_input == 1]
        outputs_list_str = [str(o).replace(":", "") for o in self.relation_toolwrapper_to_fileioinfo + self.relation_toolwrapper_to_tableioinfo if o.relation_file_or_tableioinfo_to_typeio.is_input == 0]
        params_list_str = [str(p).replace(":","") for p in self.relation_toolwrapper_to_option]
        s = ""
        s += "ToolWrapper " + self.rule_name + "\n"
        s += "ToolWrapper " + self.__class__.__name__ + "\n"
        s += "Inputs\n" + "\n\t".join(inputs_list_str) + "\n"
        s += "Outputs\n" + "\n".join(outputs_list_str) + "\n"
        s += "Parameters\n" + "\n".join(params_list_str) + "\n"
        return(s)

    def __str__(self):
        inputs_list_str = [str(i) for i in self.relation_toolwrapper_to_fileioinfo +
                           self.relation_toolwrapper_to_tableioinfo if i.relation_file_or_tableioinfo_to_typeio.is_input == 1]
        outputs_list_str = [str(o) for o in self.relation_toolwrapper_to_fileioinfo +
                            self.relation_toolwrapper_to_tableioinfo if o.relation_file_or_tableioinfo_to_typeio.is_input == 0]
        params_list_str = [str(p) for p in self.relation_toolwrapper_to_option]
        s = ""
        s += "ToolWrapper " + str(self.rule_name) + ":" + "\n"
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

    def touch(self):
        """Updates modification time of output table or file"""

        ################################################################################################################
        #
        # Touch output table
        #
        ################################################################################################################

        for output_table in [table for table in self.relation_toolwrapper_to_tableioinfo
                             if table.relation_file_or_tableioinfo_to_typeio.is_input == 0]:
            out_table_inst = SQLManager.instance().get_session().query(TableModificationTime).filter_by(table_name=output_table.table_key).first()
            timestamp_epoch_millis, timestamp_human = get_current_time()
            out_table_inst.mtime_epoch_millis = timestamp_epoch_millis
            out_table_inst.mtime_human = timestamp_human
            SQLManager.instance().get_session().commit()

        ################################################################################################################
        #
        # Touch output file
        #
        ################################################################################################################

        for output_file in [this_file for this_file in self.relation_toolwrapper_to_fileioinfo
                            if this_file.relation_file_or_tableioinfo_to_typeio.is_input == 0]:
            if not (OptionManager.instance()["--directory"] is None):
                output_file_path = os.path.join(OptionManager.instance()["--directory"], output_file.path)
            else:
                output_file_path = output_file.path
            if os.path.exists(output_file_path):
                pathlib.Path(output_file_path).touch(exist_ok=True)

    ################################################################################################################
    #
    # Methods that the developer should implement
    #
    ################################################################################################################

    def specify_input_file(self):
        """
        Should be implemented by the tool_python_path developer.

        This method return a List of string containing the input file variable names as String.
        :return: [String]
        """
        return []

    def specify_input_table(self):
        """
        Should be implemented by the tool_python_path developer.

        This method return a List of string containing the input table names names as String.
        :return: [String]
        """
        return []

    def specify_output_file(self):
        """
        Should be implemented by the tool_python_path developer.

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

        This method return a dict of string associated with string. Keys are the is_input of the relation_toolwrapper_to_option and values, their types.

        :return: {String: String}
        """
        return {}

    def run(self):
        """
        Should be implemented by the tool_python_path developer.

        The core function of the ToolWrapper is this method. It wraps the actual execution of the tool underlying the ToolWrapper.

        :raises NotImplementedError: If it doesn't have been implemented by the ToolWrapper Developer.
        """
        raise NotImplementedError("The method run of the ToolWrapper " + str(self.tool_python_path) + " should be implemented")

    ### Methods availables for the tool developer

    def input_file(self, key):
        """
        Return the path of the specified input file.

        :param key: String the is_input of the variable containing the path
        :return:
        """
        try:
            return [f.path for f in self.relation_toolwrapper_to_fileioinfo if f.file_key == key and f.relation_file_or_tableioinfo_to_typeio.is_input == 1][0]
        except IndexError:
            raise WopMarsException("Error during the execution of the ToolWrapper " + str(self.tool_python_path) +
                                   " (rule " + self.rule_name + ").",
                                   "The input file " + str(key) + " has not been specified.")

    def input_table(self, key):
        """
        Return the input table object of the given is_input.

        :param key: String: the is_input of the Table object.
        :return:
        """
        try:
            return [t for t in self.relation_toolwrapper_to_tableioinfo if t.table_key == key and t.relation_file_or_tableioinfo_to_typeio.is_input == 1][0].get_table()
        except IndexError:
            raise WopMarsException("Error during the execution of the ToolWrapper " + str(self.tool_python_path) +
                                   " (rule " + self.rule_name + ").",
                                   "The input table " + str(key) + " has not been specified.")

    def output_file(self, key):
        """
        Return the path of the specified output file.

        :param key: String the is_input of the variable containing the path
        :return:
        """
        try:
            return [f.path for f in self.relation_toolwrapper_to_fileioinfo if f.file_key == key and f.relation_file_or_tableioinfo_to_typeio.is_input == 0][0]
        except IndexError:
            raise WopMarsException("Error during the execution of the ToolWrapper " + str(self.tool_python_path) +
                                   " (rule " + self.rule_name + ").",
                                   "The output file " + str(key) + " has not been specified.")

    def output_table(self, key):
        """
        Return the output table object of the given is_input.

        :param key: String: the is_input of the Table object.
        :return:
        """
        try:
            return [t for t in self.relation_toolwrapper_to_tableioinfo if t.table_key == key and t.relation_file_or_tableioinfo_to_typeio.is_input == 0][0].get_table()
        except IndexError:
            raise WopMarsException("Error during the execution of the ToolWrapper " + str(self.tool_python_path) +
                                   " (rule " + self.rule_name + ").",
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
            value = [o.value for o in self.relation_toolwrapper_to_option if o.name == key][0]
            list_splitted_carac = self.specify_params()[key].split("|")
            for s_type in list_splitted_carac:
                s_formated_type = s_type.strip().lower()
                # check if the carac is a castable type
                if s_formated_type in Option.static_option_castable:
                    value = eval(s_formated_type)(value)
                    break
            return value
        except IndexError as e:
            # antipattern, this is bad, but I deleted the warning because if the ToolWrapper Developer put his call to
            # option in a loop, there will be too mutch output
            pass
            return None

    def session(self):
        return self.session
