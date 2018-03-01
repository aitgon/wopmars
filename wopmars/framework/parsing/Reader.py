import datetime
import importlib
#import jinja2
import re
import time
import os

import yaml
from yaml.constructor import ConstructorError
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

from sqlalchemy.orm.exc import NoResultFound, ObjectDeletedError

from wopmars.framework.database.SQLManager import SQLManager
from wopmars.framework.database.tables.Execution import Execution
from wopmars.framework.database.tables.IODbPut import IODbPut
from wopmars.framework.database.tables.IOFilePut import IOFilePut
from wopmars.framework.database.tables.ModificationTable import ModificationTable
from wopmars.framework.database.tables.Option import Option
from wopmars.framework.database.tables.Type import Type
from wopmars.utils.DictUtils import DictUtils

from wopmars.utils.Logger import Logger
from wopmars.utils.OptionManager import OptionManager
from wopmars.utils.exceptions.WopMarsException import WopMarsException


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
        self.__dict_workflow_definition = None

    def load_definition_file(self, s_definition_file):
        """
        Open the definition file and load it's content in a dictionnary thanks to the ``yaml`` library. ``yaml`` can
        raise an exception if the yaml specifications are not respected or if there is duplicates at the same level of
        hierarchy in the definition file. If so, the exception is caught then wrapped into a ``WopMarsException``.

        The check of the grammar of the definition file is done during this step but no tests are performed regarding
        to the actual content of the definition file.

        :param s_definition_file: Path to the definition file
        :type s_definition_file: str
        :raises WopMarsException: The yaml specifications are not respected
        """
        # Tests about grammar and syntax are performed here (file's existence is also tested here)
        try:
            with open(s_definition_file, 'r') as def_file:
                s_def_file_content = def_file.read()
            try:
                # The workflow definition file is loaded as-it in memory by the pyyaml library
                Logger.instance().info("Reading the Wopfile: " + str(s_definition_file))
                # Replace jinja2 variables with environment variable values
                #s_def_file_content = jinja2.Environment().from_string(s_def_file_content).render(os.environ)
                # Parse the file to find duplicates rule names (it is a double check with the following step)
                Reader.check_duplicate_rules(s_def_file_content)
                # Allows to raise an exception if duplicate keys are found on the same document hirearchy level.
                yaml.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, Reader.no_duplicates_constructor)
                # The whole content of the definition file is loaded in this dict.
                # yaml.load return None if there is no content in the String
                self.__dict_workflow_definition = yaml.load(s_def_file_content) or {}
                if self.__dict_workflow_definition == {}:
                    Logger.instance().warning("The workflow definition file is empty")
                Logger.instance().debug("\n" + DictUtils.pretty_repr(self.__dict_workflow_definition))
                Logger.instance().debug("Read complete.")
                Logger.instance().info("Checking whether the file is well formed...")
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
                                   "The specified file at " + s_definition_file + " doesn't exist.")

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
    def check_duplicate_rules(s_workflow_file):
        """
        This method raises an exception if the workflow definition file contains duplicate rule names.

        The workflow definition file should contain rules with different name. It is therefore recommended to not
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

        :param s_workflow_file: The content of the definition file
        :type s_workflow_file: str
        :raises WopMarsException: There is a duplicate rule name
        """
        Logger.instance().debug("Looking for duplicate rules...")
        # All rules are found using this regex.
        rules = re.findall(r'rule (.+?):', str(s_workflow_file))
        seen = set()
        # for each rule name
        for r in rules:
            # if the rule has not been seen before
            if r not in seen:
                # add it to the set of seen rules
                seen.add(r)
            else:
                # There is a duplicate rule name
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
            filesortables = (ni files|ni tables){0-2}
            files         = "file"  ":" (ni identifier ”:” stringliteral)+
            tables        = "table"  ":" (ni identifier ”:” stringliteral)+
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
        for s_key_step1 in self.__dict_workflow_definition:
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

            for s_key_step2 in self.__dict_workflow_definition[s_key_step1]:
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
                    for s_key_step3 in self.__dict_workflow_definition[s_key_step1][s_key_step2]:
                        if not regex_step3.search(s_key_step3):
                            raise WopMarsException("Error while parsing the configuration file: \n\t"
                                                   "The grammar of the WopMars's definition file is not respected:",
                                                   "The line containing:'" + str(s_key_step3) + "'" +
                                                   " for rule '" + str(s_key_step1) + "'" +
                                                   " doesn't match the grammar: it should be " +
                                                   "'file' or 'table'" +
                                                   "\nexemple:" + exemple_file_def)
                        elif s_key_step3 == "file":
                            for s_variable_name in self.__dict_workflow_definition[s_key_step1][s_key_step2][s_key_step3]:
                                if type(self.__dict_workflow_definition[s_key_step1][s_key_step2][s_key_step3][s_variable_name]) != str:
                                    raise WopMarsException("Error while parsing the configuration file: \n\t" +
                                                           "The grammar of the WopMars's definition file is not respected:",
                                                           "The line containing:'" + str(s_variable_name) + "'" +
                                                           " for rule '" + str(s_key_step1) + "'" +
                                                           " doesn't match the grammar: it should be the string containing the path to the file."
                                                           "\nexemple:" + exemple_file_def)
                        elif s_key_step3 == "table":
                            for s_tablename in self.__dict_workflow_definition[s_key_step1][s_key_step2][s_key_step3]:
                                if type(s_tablename) != str:
                                    raise WopMarsException("Error while parsing the configuration file: \n\t"
                                                           "The grammar of the WopMars's definition file is not respected:",
                                                           "The line containing:'" + str(s_variable_name) + "'" +
                                                           " for rule '" + str(s_key_step1) + "'" +
                                                           " doesn't match the grammar: it should be the string containing the name of the Model."
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
        Method called when the ``tool`` command is used. It is equivalent to the :meth:`~.wopmars.framework.parsing.Reader.Reader.read` method but create a workflow
        with only one toolwrapper. The workflow is also stored inside the database.

        :param s_toolwrapper: The name of the toolwrapper (will be imported)
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
            execution = Execution(started_at=datetime.datetime.fromtimestamp(time.time()))
            # get the types that should have been created previously
            input_entry = session.query(Type).filter(Type.name == "input").one()
            output_entry = session.query(Type).filter(Type.name == "output").one()

            Logger.instance().debug("Loading unique toolwrapper " + s_toolwrapper)
            dict_dict_dict_elm = dict(dict_input={"file": {}, "table": {}},
                                 dict_params={},
                                 dict_output={"file": {}, "table": {}})
            for type in dict_inputs:
                if type == "file":
                    for s_input in dict_inputs[type]:
                        obj_created = IOFilePut(name=s_input,
                                                path=os.path.abspath(os.path.join(OptionManager.instance()["--directory"],
                                                                                  dict_inputs[type][s_input])))
                        dict_dict_dict_elm["dict_input"][type][s_input] = obj_created
                        Logger.instance().debug("Object input file: " + s_input + " created.")
                elif type == "table":
                    for s_input in dict_inputs[type]:
                        obj_created = IODbPut(model=dict_inputs[type][s_input],
                                              tablename=s_input)
                        dict_dict_dict_elm["dict_input"][type][s_input] = obj_created
                        Logger.instance().debug("Object input table: " + s_input + " created.")
            for type in dict_outputs:
                if type == "file":
                    for s_output in dict_outputs[type]:
                        obj_created = IOFilePut(name=s_output,
                                                path=os.path.abspath(os.path.join(OptionManager.instance()["--directory"],
                                                                                  dict_outputs[type][s_output])))
                        dict_dict_dict_elm["dict_output"]["file"][s_output] = obj_created
                        Logger.instance().debug("Object output file: " + s_output + " created.")
                elif type == "table":
                    for s_output in dict_outputs[type]:
                        obj_created = IODbPut(model=dict_outputs[type][s_output],
                                              tablename=s_output)
                        dict_dict_dict_elm["dict_output"]["table"][s_output] = obj_created
                        Logger.instance().debug("Object output table: " + s_output + " created.")
            for s_param in dict_params:
                obj_created = Option(name=s_param,
                                     value=dict_params[s_param])
                dict_dict_dict_elm["dict_params"][s_param] = obj_created
                Logger.instance().debug("Object option: " + s_param + " created.")

            # Instantiate the refered class
            wrapper_entry = self.create_toolwrapper_entry("rule_" + s_toolwrapper, s_toolwrapper,
                                                          dict_dict_dict_elm, input_entry, output_entry)
            wrapper_entry.execution = execution
            Logger.instance().debug("Object toolwrapper: " + s_toolwrapper + " created.")
            session.add(wrapper_entry)
            session.commit()
            session.rollback()
            IODbPut.set_tables_properties(IODbPut.get_execution_tables())
            # commit /rollback trick to clean the session
            # todo ask lionel est-ce-que tu as deja eu ce problème à ne pas pouvoir faire des queries et des ajouts
            # dans la meme session?
            session.commit()
            session.rollback()
            # This create_all will create all tables that have been found in the toolwrapper
            # if not SQLManager.instance().d_database_config['db_connection'] == 'postgresql':
            # TODO: this function is not creating the triggers after the table in postgresql so I switched it off
            IODbPut.create_triggers()
            SQLManager.instance().create_all()
            wrapper_entry.is_content_respected()
        except NoResultFound as e:
            session.rollback()
            raise WopMarsException("Error while parsing the configuration file. The database has not been setUp Correctly.",
                                   str(e))

    def read(self, s_definition_file):
        """
        Reads the file given and insert the rules of the workflow in the database.

        The definition file is supposed to be properly formed. The validation of the content of the definition is done
        during the instanciation of the tools.

        :param: s_definition_file: String containing the path to the definition file.
        :type s_definition_file: str
        :raise: WopmarsException: The content is not validated
        """
        self.load_definition_file(s_definition_file)

        session = SQLManager.instance().get_session()

        # The dict_workflow_definition is assumed to be well formed
        try:
            # The same execution entry for the whole workflow-related database entries.
            execution = Execution(started_at=datetime.datetime.fromtimestamp(time.time()))
            # get the types database entries that should have been created previously
            input_entry = session.query(Type).filter(Type.name == "input").one()
            output_entry = session.query(Type).filter(Type.name == "output").one()
            set_wrapper = set()
            # Encounter a rule block
            for rule in self.__dict_workflow_definition:
                str_wrapper_name = None
                # the name of the rule is extracted after the "rule" keyword. There shouldn't be a ":" but it costs nothing.
                str_rule_name = rule.split()[-1].strip(":")
                Logger.instance().debug("Encounter rule " + str_rule_name + ": \n" +
                                        str(DictUtils.pretty_repr(self.__dict_workflow_definition[rule])))
                # The dict of "input"s, "output"s and "params" is re-initialized for each wrapper
                dict_dict_dict_elm = dict(dict_input={"file": {}, "table": {}},
                                          dict_params={},
                                          dict_output={"file": {}, "table": {}})
                for key_second_step in self.__dict_workflow_definition[rule]:
                    # key_second_step is supposed to be "tool", "input", "output" or "params"
                    if type(self.__dict_workflow_definition[rule][key_second_step]) == dict:
                        # if it is a dict, then inputs, outputs or params are coming
                        for key_third_step in self.__dict_workflow_definition[rule][key_second_step]:
                            # todo tabling modification of the indentation levels + appearance of tables in file
                            if key_second_step == "params":
                                key = key_third_step
                                value = self.__dict_workflow_definition[rule][key_second_step][key_third_step]
                                obj_created = Option(name=key,
                                                     value=value)
                                dict_dict_dict_elm["dict_params"][key] = obj_created
                            else:
                                for key_fourth_step in self.__dict_workflow_definition[rule][key_second_step][key_third_step]:
                                    obj_created = None
                                    if key_third_step == "file":
                                        key = key_fourth_step
                                        str_path_to_file = os.path.join(OptionManager.instance()["--directory"],
                                                                        self.__dict_workflow_definition[rule][
                                                                            key_second_step][
                                                                            key_third_step][
                                                                            key])
                                        obj_created = IOFilePut(name=key,
                                                                path=os.path.abspath(str_path_to_file))

                                    elif key_third_step == "table":
                                        key = key_fourth_step
                                        modelname = self.__dict_workflow_definition[rule][
                                            key_second_step][
                                            key_third_step][
                                            key]
                                        obj_created = IODbPut(model=modelname, tablename=key)

                                        dict_dict_dict_elm["dict_" + key_second_step][
                                            key_third_step][
                                            key] = self.__dict_workflow_definition[rule][key_second_step][key_third_step][key]
                                    # all elements of the current rule block are stored in there
                                    # key_second_step is input or output here
                                    dict_dict_dict_elm["dict_" + key_second_step][key_third_step][key] = obj_created
                                    Logger.instance().debug("Object " + key_second_step + " " + key_third_step + ": " +
                                                            key + " created.")
                    else:
                        # if the step is not a dict, then it is supposed to be the "tool" line
                        str_wrapper_name = self.__dict_workflow_definition[rule][key_second_step]
                # At this point, "dict_dict_dict_elm" is like this:
                # {
                #     'dict_params': {
                #         'option1': Option('option1', 'valueofoption1')
                #     },
                #     'dict_input': {
                #         'file' : {
                #             'input1': IOFilePut('input1', 'path/to/input1')
                #         }
                #         'table': {
                #             'table1': IODbPut('table1', 'package.of.table1')
                #         }
                #     },
                # }

                # Instantiate the refered class and add it to the set of objects
                wrapper_entry = self.create_toolwrapper_entry(str_rule_name, str_wrapper_name, dict_dict_dict_elm, input_entry, output_entry)
                # Associating a toolwrapper to an execution
                wrapper_entry.execution = execution
                set_wrapper.add(wrapper_entry)
                Logger.instance().debug("Object toolwrapper: " + str_wrapper_name + " created.")
                # commit/rollback trick to clean the session - SQLAchemy bug suspected
                session.commit()
                session.rollback()
                # todo set_table_properties outside the rules loop to take into account all the tables at once
                # (error if one tool has a foreign key refering to a table that is not in its I/O put
            IODbPut.set_tables_properties(IODbPut.get_execution_tables())
            session.commit()
            session.rollback()
            # This create_all will create all tables that have been found in the toolwrapper
            # if not SQLManager.instance().d_database_config['db_connection'] == 'postgresql':
            # TODO: this function is not creating the triggers after the table in postgresql so I switched it off
            IODbPut.create_triggers()
            SQLManager.instance().create_all()
            session.add_all(set_wrapper)
            # save all operations done so far.
            session.commit()
            for tw in set_wrapper:
                tw.is_content_respected()

        except NoResultFound as e:
            session.rollback()
            raise WopMarsException("Error while parsing the configuration file. The database has not been setUp Correctly.",
                                   str(e))

    def create_toolwrapper_entry(self, str_rule_name, str_wrapper_name, dict_dict_dict_elm, input_entry, output_entry):
        """
        Actual creating of the Toolwrapper object.

        The toolwrapper object is an entry of the table rule in the resulting database.

        If the scoped_session has current modification, they probably will be commited during this method:
        tables are created and this can only be done with clean session.

        :param str_rule_name: Contains the name of the rule in which the toolwrapper will be used.
        :type str_rule_name: str
        :param str_wrapper_name: Contains the name of the toolwrapper. It will be used for importing the correct module and then for creating the class
        :type str_wrapper_name: str
        :param dict_dict_dict_elm: "input"s "output"s and "params" and will be used to make relations between options / input / output and the toolwrapper.
        :type dict_dict_dict_elm: dict(dict(dict()))
        :param input_entry: input entry
        :type input_entry: :class:`wopmars.framework.bdd.tables.Type.Type`
        :param output_entry: output entry
        :type output_entry: :class:`wopmars.framework.bdd.tables.Type.Type`

        :return: TooLWrapper instance
        """
        session = SQLManager.instance().get_session()
        # Importing the module in the mod variable
        try:
            mod = importlib.import_module(str_wrapper_name)
            # Building the class object
            toolwrapper_class = eval("mod." + str_wrapper_name.split('.')[-1])
        except AttributeError:
            raise WopMarsException("Error while parsing the configuration file: \n\t",
                                   "The class " + str_wrapper_name + " doesn't exist.")
        except ImportError as IE:
            if str_wrapper_name in str(IE):
                raise WopMarsException("Error while parsing the configuration file:",
                                       str_wrapper_name + " module is not in the pythonpath. ")
            else:
                raise WopMarsException("Error while parsing the configuration file:",
                                       str_wrapper_name + " module contains an ImportError: " + str(IE))
        # Initialize the instance of ToolWrapper
        toolwrapper_wrapper = toolwrapper_class(rule_name=str_rule_name)

        # associating ToolWrapper instances with their files / tables
        for elm in dict_dict_dict_elm["dict_input"]:
            if elm == "file":
                for input_f in dict_dict_dict_elm["dict_input"][elm]:
                    # set the type of IOFilePut object
                    iofileput_entry = dict_dict_dict_elm["dict_input"][elm][input_f]
                    iofileput_entry.type = input_entry
                    try:
                        # associating file and toolwrapper
                        toolwrapper_wrapper.files.append(iofileput_entry)
                    except ObjectDeletedError as e:
                        raise WopMarsException("Error in the toolwrapper class declaration. Please, notice the developer",
                                               "The error is probably caused by the lack of the 'polymorphic_identity' attribute"
                                               " in the toolwrapper. Error message: \n" + str(e))
            elif elm == "table":
                for input_t in dict_dict_dict_elm["dict_input"][elm]:
                    # input_t is the name of the table (not the model)
                    # this is a preventing commit because next statement will create a new table and the session has to
                    # be clean. I think it is a bug in SQLAlchemy which not allows queries then insert statements in
                    # the same session
                    session.commit()
                    iodbput_entry = dict_dict_dict_elm["dict_input"][elm][input_t]
                    # the user-side tables are created during the reading of the definition file
                    # table_entry = IODbPut(name=dict_dict_dict_elm["dict_input"][elm][input_t], tablename=input_t)
                    # insert in the database the date of last modification of a developper-side table
                    modification_table_entry, created = session.get_or_create(ModificationTable,
                                                                              defaults={
                                                                                  "date": datetime.datetime.fromtimestamp(
                                                                                      time.time())},
                                                                              table_name=input_t)
                    iodbput_entry.modification = modification_table_entry
                    iodbput_entry.type = input_entry
                    try:
                        toolwrapper_wrapper.tables.append(iodbput_entry)
                    except ObjectDeletedError as e:
                        raise WopMarsException("Error in the toolwrapper class declaration. Please, notice the developer",
                                               "The error is probably caused by the lack of the 'polymorphic_identity' attribute"
                                               " in the toolwrapper. Error message: \n" + str(e))

        for elm in dict_dict_dict_elm["dict_output"]:
            if elm == "file":
                for output_f in dict_dict_dict_elm["dict_output"][elm]:
                    iofileput_entry = dict_dict_dict_elm["dict_output"][elm][output_f]
                    iofileput_entry.type = output_entry
                    try:
                        toolwrapper_wrapper.files.append(iofileput_entry)
                    except ObjectDeletedError as e:
                        raise WopMarsException("Error in the toolwrapper class declaration. Please, notice the developer",
                                               "The error is probably caused by the lack of the 'polymorphic_identity' attribute"
                                               " in the toolwrapper. Error message: \n" + str(e))
            elif elm == "table":
                for output_t in dict_dict_dict_elm["dict_output"][elm]:
                    # output_t is the table name (not the model)
                    session.commit()
                    iodbput_entry = dict_dict_dict_elm["dict_output"][elm][output_t]
                    modification_table_entry, created = session.get_or_create(ModificationTable,
                                                                              defaults={
                                                                                  "date": datetime.datetime.fromtimestamp(
                                                                                      time.time())},
                                                                              table_name=output_t)
                    iodbput_entry.modification = modification_table_entry
                    iodbput_entry.type = output_entry
                    try:
                        toolwrapper_wrapper.tables.append(iodbput_entry)
                    except ObjectDeletedError as e:
                        raise WopMarsException(
                            "Error in the toolwrapper class declaration. Please, notice the developer",
                            "The error is probably caused by the lack of the 'polymorphic_identity' attribute"
                            " in the toolwrapper. Error message: \n" + str(
                                e))

        for opt in dict_dict_dict_elm["dict_params"]:
            # associating option and toolwrapper
            toolwrapper_wrapper.options.append(dict_dict_dict_elm["dict_params"][opt])

        # toolwrapper_wrapper.is_content_respected()
        return toolwrapper_wrapper
