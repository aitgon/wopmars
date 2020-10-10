import importlib
import re
import os

import yaml
from yaml.constructor import ConstructorError

from wopmars.utils.various import get_current_time

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

from sqlalchemy.orm.exc import NoResultFound, ObjectDeletedError

from wopmars.SQLManager import SQLManager
from wopmars.models.Execution import Execution
from wopmars.models.TableInputOutputInformation import TableInputOutputInformation
from wopmars.models.FileInputOutputInformation import FileInputOutputInformation
from wopmars.models.TableModificationTime import TableModificationTime
from wopmars.models.Option import Option
from wopmars.models.TypeInputOrOutput import TypeInputOrOutput
from wopmars.utils.DictUtils import DictUtils
from wopmars.utils.Logger import Logger
from wopmars.utils.OptionManager import OptionManager
from wopmars.utils.WopMarsException import WopMarsException


class Reader:
    """
    This class is responsible of the parsing of the user's entries:

     - the arguments given with the ``tool`` command
     - the content of the workflow definition file, in normal mode

    This module uses the ``yaml`` library in order to parse the workflow definition file. Some additional rules have been
    added to the ``yaml`` library in order to prevent duplicate rules.

    Also, once the ``Reader`` has gotten the workflow definition informations, it'll check for eventual errors and then
    store them in the database. Those stored informations are what we call the "history" of **WoPMaRS**.
    """
    def __init__(self):
        self.__wopfile_yml_dict = None

    def load_wopfile_as_yml_dic(self, wopfile_path):
        """
        Open the definition file and load it's content in a dictionnary thanks to the ``yaml`` library. ``yaml`` can
        raise an exception if the yaml specifications are not respected or if there is duplicates at the same level of
        hierarchy in the definition file. If so, the exception is caught then wrapped into a ``WopMarsException``.

        The check of the grammar of the definition file is done during this step but no tests are performed regarding
        to the actual content of the definition file.

        :param wopfile_path: Path to the definition file
        :type wopfile_path: str
        :raises WopMarsException: The yaml specifications are not respected
        """
        # Tests about grammar and syntax are performed here (file's existence is also tested here)
        try:
            with open(wopfile_path, 'r') as def_file:
                wopfile_content_str = def_file.read()
            try:
                # The workflow definition file is loaded as-it in memory by the pyyaml library
                Logger.instance().info("Reading the Wopfile.yml: " + str(wopfile_path))
                # Replace jinja2 variables with environment variable values
                #s_def_file_content = jinja2.Environment().from_string(s_def_file_content).render(os.environ)
                # Parse the file to find duplicates rule names (it is a double check with the following step)
                Reader.check_duplicate_rules(wopfile_content_str)
                # Allows to raise an exception if duplicate keys are found on the same document hirearchy level.
                yaml.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, Reader.no_duplicates_constructor)
                # The whole content of the definition file is loaded in this dict.
                # yaml.load return None if there is no content in the String
                self.__wopfile_yml_dict = yaml.load(wopfile_content_str, Loader=yaml.SafeLoader) or {}
                if self.__wopfile_yml_dict == {}:
                    Logger.instance().warning("The workflow definition file is empty")
                Logger.instance().debug("\n" + DictUtils.pretty_repr(self.__wopfile_yml_dict))
                Logger.instance().debug("Read complete.")
                Logger.instance().debug("Checking whether the file is well formed...")
                # raise an exception if there is a problem with the grammar
                self.is_grammar_respected()
                Logger.instance().debug("File well formed.")
            # YAMLError is thrown if the YAML specifications are not respected by the definition file
            except yaml.YAMLError as exc:
                raise WopMarsException("Error while parsing the configuration file: \n\t"
                                       "The YAML specification is not respected:", str(exc))
            except ConstructorError as CE:
                raise WopMarsException("Error while parsing the configuration file: \n\t",
                                       str(CE))
        except FileNotFoundError:
            raise WopMarsException("Error while parsing the configuration file: \n\tInput error:",
                                   "The specified file at " + wopfile_path + " doesn't exist.")

    # Code from the github: https://gist.github.com/pypt/94d747fe5180851196eb
    @staticmethod
    def no_duplicates_constructor(loader, node, deep=False):
        """
        Make the yaml constructor to check for duplicate keys.
        """
        mapping = {}
        for key_node, value_node in node.value:
            key = loader.construct_object(key_node, deep=deep)
            value = loader.construct_object(value_node, deep=deep)
            if key in mapping:
                raise ConstructorError("while constructing a mapping", node.start_mark,
                                       "found duplicate key (%s)" % key, key_node.start_mark)
            mapping[key] = value
        return loader.construct_mapping(node, deep)

    @staticmethod
    def check_duplicate_rules(wopfile_content_str):
        """
        This method raises an exception if the workflow definition file contains duplicate rule names.

        The workflow definition file should contain rules with different is_input. It is therefore recommended to not
        call rules with tool names but functionality instead. Example:

            .. code-block:: yaml

                rule get_snp:
                    tool: SNPGetter
                    input:
                        file:
                            etc..
                        table:
                            etc..
                    output:
                        file:
                            etc..
                        table:
                            etc..
                    params:
                        etc..

        :param wopfile_content_str: The content of the definition file
        :type wopfile_content_str: str
        :raises WopMarsException: There is a duplicate rule is_input
        """
        Logger.instance().debug("Looking for duplicate rules...")
        # All rules are found using this regex.
        rules = re.findall(r'rule (.+?):', str(wopfile_content_str))
        seen = set()
        # for each rule is_input
        for r in rules:
            # if the rule has not been seen before
            if r not in seen:
                # add it to the set of seen rules
                seen.add(r)
            else:
                # There is a duplicate rule is_input
                raise WopMarsException("Error while parsing the configuration file:\n\t",
                                       "The rule " + r + " is duplicated.")
        Logger.instance().debug("No Duplicate.")

    def is_grammar_respected(self):
        """
        Check if the definition file respects the grammar. Throw a WopMarsException exception if not.

        The formal representation of the grammar is::

            WoPMaRS       = rule
            identifier    = String
            ni            = NEWLINE INDENT
            rule          = "rule" identifier ":" ruleparams
            ruleparams    = [ni tool] [ni input] [ni output] [ni params]
            filesortables = (ni files|ni models){0-2}
            files         = "file"  ":" (ni identifier ”:” stringliteral)+
            models        = "table"  ":" (ni identifier ”:” stringliteral)+
            tool          = "tool"   ":" stringliteral
            input         = "input"  ":" ni filesortables
            output        = "output" ":" ni filesortables
            params        = "params" ":" (ni identifier ”:” stringliteral)+
            (NEWLINE WoPMaRS)+

        :raises WopMarsException: The grammar is not respected
        """
        exemple_file_def = """
    rule RULENAME:
        tool: TOOLNAME
        input:
            file:
                INPUTNAME: INPUTVALUE
            table:
                - path.to.table
        output:
            file:
                OUTPUTNAME: OUTPUTVALUE
            table:
                - path.to.table
        params:
            OPTIONNAME: OPTIONVALUE

    rule ...etc...
        """
        # recognize the rule blocks
        regex_step1 = re.compile(r"(^rule [^\s]+$)")

        # recognize the elements of the rule
        regex_step2 = re.compile(r"(^params$)|(^tool$)|(^input$)|(^output$)")

        # recognize the file/table blocks
        regex_step3 = re.compile(r"(^file$)|(^table$)")

        # The words found are tested against the regex to see if they match or not
        for s_key_step1 in self.__wopfile_yml_dict:
            bool_toolwrapper = False
            # The first level of indentation should only contain rules
            if not regex_step1.search(s_key_step1):
                raise WopMarsException("Error while parsing the configuration file: \n\t"
                                       "The grammar of the WopMars's definition file is not respected:",
                                       "The line containing:\'" +
                                       str(s_key_step1) +
                                       "\' doesn't match the grammar: it should start with 'rule'" +
                                       "and contains only one word after the 'rule' keyword" +
                                       "\nexemple:" + exemple_file_def)

            for s_key_step2 in self.__wopfile_yml_dict[s_key_step1]:
                # the second level of indentation should only contain elements of rule
                if not regex_step2.search(s_key_step2):
                    raise WopMarsException("Error while parsing the configuration file: \n\t"
                                           "The grammar of the WopMars's definition file is not respected:",
                                           "The line containing:'" + str(s_key_step2) + "'" +
                                           " for rule '" + str(s_key_step1) + "'" +
                                           " doesn't match the grammar: it should be " +
                                           "'tool', 'params', 'input' or 'output'" +
                                           "\nexemple:" + exemple_file_def)
                elif s_key_step2 == "input" or s_key_step2 == "output":
                    for s_key_step3 in self.__wopfile_yml_dict[s_key_step1][s_key_step2]:
                        if not regex_step3.search(s_key_step3):
                            raise WopMarsException("Error while parsing the configuration file: \n\t"
                                                   "The grammar of the WopMars's definition file is not respected:",
                                                   "The line containing:'" + str(s_key_step3) + "'" +
                                                   " for rule '" + str(s_key_step1) + "'" +
                                                   " doesn't match the grammar: it should be " +
                                                   "'file' or 'table'" +
                                                   "\nexemple:" + exemple_file_def)
                        elif s_key_step3 == "file":
                            for s_variable_name in self.__wopfile_yml_dict[s_key_step1][s_key_step2][s_key_step3]:
                                if type(self.__wopfile_yml_dict[s_key_step1][s_key_step2][s_key_step3][s_variable_name]) != str:
                                    raise WopMarsException("Error while parsing the configuration file: \n\t" +
                                                           "The grammar of the WopMars's definition file is not respected:",
                                                           "The line containing:'" + str(s_variable_name) + "'" +
                                                           " for rule '" + str(s_key_step1) + "'" +
                                                           " doesn't match the grammar: it should be the string containing the path to the file."
                                                           "\nexemple:" + exemple_file_def)
                        elif s_key_step3 == "table":
                            for s_tablename in self.__wopfile_yml_dict[s_key_step1][s_key_step2][s_key_step3]:
                                if type(s_tablename) != str:
                                    raise WopMarsException("Error while parsing the configuration file: \n\t"
                                                           "The grammar of the WopMars's definition file is not respected:",
                                                           "The line containing:'" + str(s_variable_name) + "'" +
                                                           " for rule '" + str(s_key_step1) + "'" +
                                                           " doesn't match the grammar: it should be the string containing the is_input of the Model."
                                                           "\nexemple:" + exemple_file_def)

                # There should be one tool at max in each rule
                elif s_key_step2 == "tool":
                    if bool_toolwrapper == False:
                        bool_toolwrapper = True
                    elif bool_toolwrapper == True:
                        raise WopMarsException("Error while parsing the configuration file: \n\t",
                                               "There is multiple tools specified for the " + str(s_key_step1))

            # All rules should contain a tool
            if not bool_toolwrapper:
                raise WopMarsException("Error while parsing the configuration file: \n\t"
                                       "The grammar of the WopMars's definition file is not respected:",
                                       "The rule '" + str(s_key_step1) + "' doesn't contain any tool." +
                                       "\nexemple:" + exemple_file_def
                                       )

    def load_one_toolwrapper(self, s_toolwrapper, s_dict_inputs, s_dict_outputs, s_dict_params):
        """
        Method called when the ``tool`` command is used. It is equivalent to the :meth:`~.wopmars.framework.parsing.Reader.Reader.iterate_wopfile_yml_dic_and_insert_rules_in_db` method but create a workflow
        with only one tool_python_path. The workflow is also stored inside the database.

        :param s_toolwrapper: The is_input of the tool_python_path (will be imported)
        :type s_toolwrapper: str
        :param s_dict_inputs: A string containing the dict of input files
        :type s_dict_inputs: str
        :param s_dict_outputs: A string containing the dict of output files
        :type s_dict_outputs: str
        :param s_dict_params: A string containing the dict of params
        :type s_dict_params: str

        :raise WopMarsException: There is an error while accessing the database
        """
        session = SQLManager.instance().get_session()
        dict_inputs = dict(eval(s_dict_inputs))
        dict_outputs = dict(eval(s_dict_outputs))
        dict_params = dict(eval(s_dict_params))
        try:
            # The same execution entry for the whole workflow-related database entries.
            time_unix_ms, time_human = get_current_time()
            execution = Execution(started_at=time_human)
            # get the types that should have been created previously
            input_entry = session.query(TypeInputOrOutput).filter(TypeInputOrOutput.is_input == True).one()
            output_entry = session.query(TypeInputOrOutput).filter(TypeInputOrOutput.is_input == False).one()

            Logger.instance().debug("Loading unique tool_python_path " + s_toolwrapper)
            dict_dict_dict_elm = dict(dict_input={"file": {}, "table": {}},
                                 dict_params={},
                                 dict_output={"file": {}, "table": {}})
            for type in dict_inputs:
                if type == "file":
                    for s_input in dict_inputs[type]:
                        obj_created = FileInputOutputInformation(file_key=s_input,
                                                                 path=os.path.join(OptionManager.instance()["--directory"],
                                                                                  dict_inputs[type][s_input]))
                        dict_dict_dict_elm["dict_input"][type][s_input] = obj_created
                        Logger.instance().debug("Object input file: " + s_input + " created.")
                elif type == "table":
                    for s_input in dict_inputs[type]:
                        model_py_path = dict_inputs[type][s_input]
                        table_name = model_py_path.split('.')[-1]
                        obj_created = TableInputOutputInformation(model_py_path=model_py_path, table_key=s_input,
                                                                  table_name=table_name)
                        dict_dict_dict_elm["dict_input"][type][s_input] = obj_created
                        Logger.instance().debug("Object input table: " + s_input + " created.")
            for type in dict_outputs:
                if type == "file":
                    for s_output in dict_outputs[type]:
                        obj_created = FileInputOutputInformation(file_key=s_output, path=dict_outputs[type][s_output])
                        dict_dict_dict_elm["dict_output"]["file"][s_output] = obj_created
                        Logger.instance().debug("Object output file: " + s_output + " created.")
                elif type == "table":
                    for s_output in dict_outputs[type]:
                        model_py_path = dict_outputs[type][s_output]
                        table_name = model_py_path.split('.')[-1]
                        obj_created = TableInputOutputInformation(model_py_path=model_py_path, table_key=s_output,
                                                                  table_name=table_name)
                        dict_dict_dict_elm["dict_output"]["table"][s_output] = obj_created
                        Logger.instance().debug("Object output table: " + s_output + " created.")
            for s_param in dict_params:
                obj_created = Option(name=s_param,
                                     value=dict_params[s_param])
                dict_dict_dict_elm["dict_params"][s_param] = obj_created
                Logger.instance().debug("Object option: " + s_param + " created.")

            # Instantiate the refered class
            wrapper_entry = self.create_tool_wrapper_inst("rule_" + s_toolwrapper, s_toolwrapper,
                                                          dict_dict_dict_elm, input_entry, output_entry)
            wrapper_entry.relation_toolwrapper_to_execution = execution
            Logger.instance().debug("Object tool_python_path: " + s_toolwrapper + " created.")
            session.add(wrapper_entry)
            session.commit()
            session.rollback()
            TableInputOutputInformation.set_tables_properties(TableInputOutputInformation.get_execution_tables())
            # commit /rollback trick to clean the session
            # totodo LucG ask lionel est-ce-que tu as deja eu ce problème à ne pas pouvoir faire des queries et des ajouts
            # dans la meme session?
            session.commit()
            session.rollback()
            # if not SQLManager.instance().d_database_config['db_connection'] == 'postgresql':
            # This command will create all the triggers that will create timestamp after modification
            TableModificationTime.create_triggers()
            # This create_all will create all models that have been found in the tool_python_path
            SQLManager.instance().create_all()
            wrapper_entry.is_content_respected()
        except NoResultFound as e:
            session.rollback()
            raise WopMarsException("Error while parsing the configuration file. The database has not been setUp Correctly.",
                                   str(e))

    def iterate_wopfile_yml_dic_and_insert_rules_in_db(self, wopfile_path):
        """
        Reads the file given and insert the rules of the workflow in the database.

        The definition file is supposed to be properly formed. The validation of the content of the definition is done
        during the instanciation of the tools.

        :param: s_definition_file: String containing the path to the definition file.
        :type wopfile_path: str
        :raise: WopmarsException: The content is not validated
        """
        self.load_wopfile_as_yml_dic(wopfile_path)

        session = SQLManager.instance().get_session()

        # The dict_workflow_definition is assumed to be well formed
        try:
            # The same execution entry for the whole workflow-related database entries.
            time_unix_ms, time_human = get_current_time()
            execution = Execution(started_at=time_human)
            # get the types database entries that should have been created previously
            input_entry = session.query(TypeInputOrOutput).filter(TypeInputOrOutput.is_input == True).one()
            output_entry = session.query(TypeInputOrOutput).filter(TypeInputOrOutput.is_input == False).one()
            tool_wrapper_set = set()
            # Encounter a rule block
            for yml_key_level1 in self.__wopfile_yml_dict:
                tool_wrapper_py_path = None
                # the is_input of the rule is extracted after the "rule" keyword. There shouldn't be a ":" but it costs nothing.
                rule_name_str = yml_key_level1.split()[-1].strip(":")
                Logger.instance().debug("Encounter rule " + rule_name_str + ": \n" +
                                        str(DictUtils.pretty_repr(self.__wopfile_yml_dict[yml_key_level1])))
                # The dict of "input"s, "output"s and "params" is re-initialized for each tool wrapper
                tool_wrapper_inst_dic = dict(dict_input={"file": {}, "table": {}}, dict_params={}, dict_output={"file": {}, "table": {}})
                for yml_key_level2 in self.__wopfile_yml_dict[yml_key_level1]:
                    # key_second_step is supposed to be "tool", "input", "output" or "params"
                    # if type(self.__wopfile_yml_dict[rule_header][yml_key_level_2nd]) == dict:
                    if yml_key_level2 in {"input", "output", "params"}:
                        # if it is a dict, then inputs, outputs or params are coming
                        for yml_key_level3 in self.__wopfile_yml_dict[yml_key_level1][yml_key_level2]:
                            if yml_key_level2 == "params":
                                # yml_key = yml_key_level3
                                value = self.__wopfile_yml_dict[yml_key_level1][yml_key_level2][yml_key_level3]
                                option_inst = Option(name=yml_key_level3, value=value)
                                tool_wrapper_inst_dic["dict_params"][yml_key_level3] = option_inst
                            else: # file or table
                                for yml_key_level4 in self.__wopfile_yml_dict[yml_key_level1][yml_key_level2][yml_key_level3]:
                                    file_or_table_inst = None
                                    if yml_key_level3 == "file":
                                        # yml_key = yml_key_level4
                                        # str_path_to_file = os.path.join(OptionManager.instance()["--directory"],
                                        #                                 self.__wopfile_yml_dict[rule][
                                        #                                     key_second_step][key_third_step][key])
                                        str_path_to_file = self.__wopfile_yml_dict[yml_key_level1][yml_key_level2][yml_key_level3][yml_key_level4]
                                        file_or_table_inst = FileInputOutputInformation(file_key=yml_key_level4, path=str_path_to_file)

                                    elif yml_key_level3 == "table":
                                        yml_key = yml_key_level4
                                        modelname = self.__wopfile_yml_dict[yml_key_level1][yml_key_level2][
                                            yml_key_level3][
                                            yml_key]
                                        model_py_path = modelname
                                        table_name = model_py_path.split('.')[-1]
                                        file_or_table_inst = TableInputOutputInformation(model_py_path=model_py_path,
                                                                                  table_key=yml_key_level4, table_name=table_name)

                                    # all elements of the current rule block are stored in there
                                    # key_second_step is input or output here
                                    # tool_wrapper_inst_dic["dict_" + yml_key_level2][yml_key_level3][yml_key] = obj_created
                                    tool_wrapper_inst_dic["dict_" + yml_key_level2][yml_key_level3][yml_key_level4] \
                                        = file_or_table_inst
                                    Logger.instance().debug("Object " + yml_key_level2 + " " + yml_key_level3 + ": " +
                                                            yml_key_level4 + " created.")
                    else:
                        # if the step is not a dict, then it is supposed to be the "tool" line
                        tool_wrapper_py_path = self.__wopfile_yml_dict[yml_key_level1][yml_key_level2]
                # At this point, "tool_wrapper_inst_dic" is like this:
                # {
                #     'dict_params': {
                #         'option1': Option('option1', 'valueofoption1')
                #     },
                #     'dict_input': {
                #         'file' : {
                #             'input1': FileInputOutputInformation('input1', 'path/to/input1')
                #         }
                #         'table': {
                #             'table1': TableInputOutputInformation('table1', 'package.of.table1')
                #         }
                #     },
                # }

                # Instantiate the referred class and add it to the set of objects
                tool_wrapper_inst = self.create_tool_wrapper_inst(rule_name_str, tool_wrapper_py_path, tool_wrapper_inst_dic,
                                                              input_entry, output_entry)
                # Associating a tool_python_path to an execution
                tool_wrapper_inst.relation_toolwrapper_to_execution = execution
                tool_wrapper_set.add(tool_wrapper_inst)
                Logger.instance().debug("Instance tool_python_path: " + tool_wrapper_py_path + " created.")
                # commit/rollback trick to clean the session - SQLAchemy bug suspected
                session.commit()
                session.rollback()
                # totodo LucG set_table_properties outside the rules loop to take into account all the models at once
                # (error if one tool has a foreign key refering to a table that is not in its I/O put
            TableInputOutputInformation.set_tables_properties(TableInputOutputInformation.get_execution_tables())
            session.commit()
            session.rollback()
            # This command is creating the triggers that will update the modification
            TableModificationTime.create_triggers()
            # This create_all will create all models that have been found in the tool_python_path
            SQLManager.instance().create_all()
            session.add_all(tool_wrapper_set)
            # save all operations done so far.
            session.commit()
            for tool_wrapper in tool_wrapper_set:
                tool_wrapper.is_content_respected()

        except NoResultFound as e:
            session.rollback()
            raise WopMarsException("Error while parsing the configuration file. The database has not been setUp Correctly.",
                                   str(e))

    def create_tool_wrapper_inst(self, rule_name, tool_python_path, dict_dict_dict_elm, input_entry, output_entry):
        """
        Actual creating of the Toolwrapper object.

        The tool_python_path object is an entry of the table rule in the resulting database.

        If the scoped_session has current modification, they probably will be commited during this method:
        models are created and this can only be done with clean session.

        :param rule_name: Contains the is_input of the rule in which the tool_python_path will be used.
        :type rule_name: str
        :param tool_python_path: Contains the is_input of the tool_python_path. It will be used for importing the correct module and then for creating the class
        :type tool_python_path: str
        :param dict_dict_dict_elm: "input"s "output"s and "params" and will be used to make relations between options / input / output and the tool_python_path.
        :type dict_dict_dict_elm: dict(dict(dict()))
        :param input_entry: input entry
        :type input_entry: :class:`wopmars.framework.bdd.models.TypeInputOrOutput.TypeInputOrOutput`
        :param output_entry: output entry
        :type output_entry: :class:`wopmars.framework.bdd.models.TypeInputOrOutput.TypeInputOrOutput`

        :return: TooLWrapper instance
        """
        session = SQLManager.instance().get_session()
        # Importing the module in the mod variable
        try:
            mod = importlib.import_module(tool_python_path)
            # Building the class object
            ToolWrapper_class = eval("mod." + tool_python_path.split('.')[-1])
        except AttributeError:
            raise WopMarsException("Error while parsing the configuration file: \n\t",
                                   "The class " + tool_python_path + " doesn't exist.")
        except ImportError as IE:
            if tool_python_path in str(IE):
                raise WopMarsException("Error while parsing the configuration file:",
                                       tool_python_path + " module is not in the pythonpath. ")
            else:
                raise WopMarsException("Error while parsing the configuration file:",
                                       tool_python_path + " module contains an ImportError: " + str(IE))
        # Initialize the instance of the user ToolWrapper
        tool_wrapper_inst = ToolWrapper_class(rule_name=rule_name)

        # associating ToolWrapper instances with their files / models
        for elm in dict_dict_dict_elm["dict_input"]:
            if elm == "file":
                for input_f in dict_dict_dict_elm["dict_input"][elm]:
                    # set the type of FileInputOutputInformation object
                    iofileput_entry = dict_dict_dict_elm["dict_input"][elm][input_f]
                    iofileput_entry.relation_file_or_tableioinfo_to_typeio = input_entry
                    try:
                        # associating file and tool_python_path
                        tool_wrapper_inst.relation_toolwrapper_to_fileioinfo.append(iofileput_entry)
                    except ObjectDeletedError as e:
                        raise WopMarsException("Error in the tool_python_path class declaration. Please, notice the developer",
                                               "The error is probably caused by the lack of the 'polymorphic_identity' attribute"
                                               " in the tool_python_path. Error message: \n" + str(e))
            elif elm == "table":
                for input_t in dict_dict_dict_elm["dict_input"][elm]:
                    # input_t is the is_input of the table (not the model)
                    # this is a preventing commit because next statement will create a new table and the session has to
                    # be clean. I think it is a bug in SQLAlchemy which not allows queries then insert statements in
                    # the same session
                    session.commit()
                    iodbput_entry = dict_dict_dict_elm["dict_input"][elm][input_t]
                    # the user-side models are created during the reading of the definition file
                    # table_entry = TableInputOutputInformation(is_input=dict_dict_dict_elm["dict_input"][elm][input_t], tablename=input_t)
                    # insert in the database the mtime_epoch_millis of last modification of a developper-side table
                    time_unix_ms, time_human = get_current_time()
                    model_py_path_suffix = dict_dict_dict_elm["dict_input"][elm][input_t].model_py_path.split('.')[-1]
                    modification_table_entry, created = session.get_or_create(TableModificationTime,
                                                                              defaults={
                                                                                  "mtime_epoch_millis": time_unix_ms,
                                                                                  "mtime_human": time_human},
                                                                              table_name=model_py_path_suffix)
                    iodbput_entry.relation_tableioinfo_to_tablemodiftime = modification_table_entry
                    iodbput_entry.relation_file_or_tableioinfo_to_typeio = input_entry
                    try:
                        tool_wrapper_inst.relation_toolwrapper_to_tableioinfo.append(iodbput_entry)
                    except ObjectDeletedError as e:
                        raise WopMarsException("Error in the tool_python_path class declaration. Please, notice the developer",
                                               "The error is probably caused by the lack of the 'polymorphic_identity' attribute"
                                               " in the tool_python_path. Error message: \n" + str(e))

        for elm in dict_dict_dict_elm["dict_output"]:
            if elm == "file":
                for output_f in dict_dict_dict_elm["dict_output"][elm]:
                    iofileput_entry = dict_dict_dict_elm["dict_output"][elm][output_f]
                    iofileput_entry.relation_file_or_tableioinfo_to_typeio = output_entry
                    try:
                        tool_wrapper_inst.relation_toolwrapper_to_fileioinfo.append(iofileput_entry)
                    except ObjectDeletedError as e:
                        raise WopMarsException("Error in the tool_python_path class declaration. Please, notice the developer",
                                               "The error is probably caused by the lack of the 'polymorphic_identity' attribute"
                                               " in the tool_python_path. Error message: \n" + str(e))
            elif elm == "table":
                for output_t in dict_dict_dict_elm["dict_output"][elm]:
                    # output_t is the table is_input (not the model)
                    session.commit()
                    iodbput_entry = dict_dict_dict_elm["dict_output"][elm][output_t]
                    time_unix_ms, time_human = get_current_time()
                    # This corresponds the __tablename__ of the database in the database
                    model_py_path_suffix = dict_dict_dict_elm["dict_output"][elm][output_t].model_py_path.split('.')[-1]
                    modification_table_entry, created = session.get_or_create(TableModificationTime,
                                                                              defaults={
                                                                                  "mtime_epoch_millis": time_unix_ms,
                                                                                  "mtime_human": time_human},
                                                                              table_name=model_py_path_suffix)
                    iodbput_entry.relation_tableioinfo_to_tablemodiftime = modification_table_entry
                    iodbput_entry.relation_file_or_tableioinfo_to_typeio = output_entry
                    try:
                        tool_wrapper_inst.relation_toolwrapper_to_tableioinfo.append(iodbput_entry)
                    except ObjectDeletedError as e:
                        raise WopMarsException(
                            "Error in the tool_python_path class declaration. Please, notice the developer",
                            "The error is probably caused by the lack of the 'polymorphic_identity' attribute"
                            " in the tool_python_path. Error message: \n" + str(
                                e))

        for opt in dict_dict_dict_elm["dict_params"]:
            # associating option and tool_python_path
            tool_wrapper_inst.relation_toolwrapper_to_option.append(dict_dict_dict_elm["dict_params"][opt])

        # toolwrapper_wrapper.is_content_respected()
        return tool_wrapper_inst
