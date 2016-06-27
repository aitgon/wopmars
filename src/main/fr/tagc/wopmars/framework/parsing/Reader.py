"""
This module contains the Reader class
"""
import datetime
import importlib
import re

import time

import os
import yaml
from yaml.constructor import ConstructorError
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

from sqlalchemy.orm.exc import NoResultFound

from src.main.fr.tagc.wopmars.framework.bdd.SQLManager import SQLManager
from src.main.fr.tagc.wopmars.framework.bdd.tables.Execution import Execution
from src.main.fr.tagc.wopmars.framework.bdd.tables.IODbPut import IODbPut
from src.main.fr.tagc.wopmars.framework.bdd.tables.IOFilePut import IOFilePut
from src.main.fr.tagc.wopmars.framework.bdd.tables.ModificationTable import ModificationTable

from src.main.fr.tagc.wopmars.framework.bdd.tables.Option import Option
from src.main.fr.tagc.wopmars.framework.bdd.tables.Type import Type
from src.main.fr.tagc.wopmars.utils.DictUtils import DictUtils
from src.main.fr.tagc.wopmars.utils.Logger import Logger
from src.main.fr.tagc.wopmars.utils.OptionManager import OptionManager
from src.main.fr.tagc.wopmars.utils.exceptions.WopMarsException import WopMarsException


class Reader:
    """
    The reader class is used to read the workflow definition file,
    build the ToolWrapper objects and perform tests on the quality
    of the definition file.
    """
    def __init__(self, s_definition_file):
        """
        Constructor of the reader.

        Open the definition file and load it's content in a dictionnary thanks to the PyYaml library. If PyYaml raise
        an exception, a WopMarsParsingException is raised instead.

        The definition file is parsed in order to find duplicates rules if there is.
        The method is_grammar_respected is called and can raise WopMarsParsingException too.

        :raise: WopMarsParsingException: if the Yaml Spec are not respected
        :param: s_definition_file: String: the definition file open in read mode
        """
        # Tests about grammar and syntax are performed here (file's existence is also tested here)
        try:
            with open(s_definition_file, 'r') as def_file:
                s_def_file_content = def_file.read()
            try:
                # The workflow definition file is loaded as-it in memory by the pyyaml library
                Logger.instance().info("Reading the definition file: " + str(s_definition_file) + "...")
                Reader.check_duplicate_rules(s_def_file_content)
                yaml.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, self.no_duplicates_constructor)
                self.__dict_workflow_definition = yaml.load(s_def_file_content)
                Logger.instance().debug("\n" + DictUtils.pretty_repr(self.__dict_workflow_definition))
                Logger.instance().info("Read complete.")
                Logger.instance().info("Checking whether the file is well formed...")
                # raise an exception if there is a problem
                self.is_grammar_respected()
                Logger.instance().info("File well formed.")
            # YAMLError is thrown if the YAML specifications are not respected by the definition file
            except yaml.YAMLError as exc:
                raise WopMarsException("Error while parsing the configuration file: \n\t"
                                       "The YAML specification is not respected:", str(exc))
            except ConstructorError as CE:
                raise WopMarsException("Error while parsing the configuration filer: \n\t",
                                       str(CE))
        except FileNotFoundError:
            raise WopMarsException("Error while parsing the configuration file: \n\tInput error:",
                                   "The specified file at " + s_definition_file + " doesn't exist.")

    @staticmethod
    def no_duplicates_constructor(loader, node, deep=False):
        """Check for duplicate keys."""

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
    def check_duplicate_rules(file):
        """
        This method raises an exception if the workflow definition file contains duplicate keys.

        The workflow definition file should contain rules with different name. It is therefore recommended to not
        call rules with tool names but functionnality instead. Example:

        rule get_snp:
            tool: SNPGetter
            input:
                etc..
            output:
                etc..
            params:
                etc..

        :param file: String this is the content of the definition file
        :return:
        """
        Logger.instance().debug("Looking for duplicate rules...")
        # All rules are found using this regex.
        rules = re.findall(r'rule (.+?):', str(file))
        seen = set()
        for r in rules:
            if r not in seen:
                seen.add(r)
            else:
                raise WopMarsException("Error while parsing the configuration file:\n\t",
                                       "The rule " + r + " is duplicated.")
        Logger.instance().debug("No Duplicate.")

    def read(self):
        """
        Reads the file and build the workflow in the database.

        ToolWrappers are then gotten from the database.

        The definition file is supposed to be properly formed. The validation of the content of the definition is done
        during the instanciation of the tools.

        :return: The set of builded ToolWrappers
        """
        session = SQLManager.instance().get_session()

        try:
            # The same execution entry for the whole workflow-related bdd entries.
            execution = Execution()
            # get the types that should have been created previously
            input_entry = session.query(Type).filter(Type.name == "input").one()
            output_entry = session.query(Type).filter(Type.name == "output").one()
            set_wrapper = set()
            # Encounter a rule block
            for rule in self.__dict_workflow_definition:
                str_wrapper_name = None
                # the name of the rule is extracted after the "rule" keyword
                str_rule_name = rule.split()[-1].strip(":")
                Logger.instance().debug("Encounter rule " + str_rule_name + ": \n" +
                                        str(DictUtils.pretty_repr(self.__dict_workflow_definition[rule])))
                # The dict of "input"s, "output"s and "params" is re-initialized for each wrapper
                dict_dict_elm = dict(dict_input={}, dict_params={}, dict_output={})
                for key_second_step in self.__dict_workflow_definition[rule]:
                    # key_second_step is supposed to be "tool", "input", "output" or "params"
                    if type(self.__dict_workflow_definition[rule][key_second_step]) == dict:
                        # if it is a dict, then inputs, outputs or params are coming
                        for elm in self.__dict_workflow_definition[rule][key_second_step]:
                            # The 2 possible objects can be created
                            if key_second_step == "params":
                                obj_created = Option(name=elm,
                                                     value=self.__dict_workflow_definition[rule][key_second_step][elm])
                            else:
                                # In theory, there cannot be a IODbPut specification in the definition file
                                obj_created = IOFilePut(name=elm,
                                                        path=os.path.abspath(os.path.join(OptionManager.instance()["--directory"], self.__dict_workflow_definition[rule][key_second_step][elm])))
                            dict_dict_elm["dict_" + key_second_step][elm] = obj_created
                            Logger.instance().debug("Object " + key_second_step + ": " +
                                                    elm + " created.")
                    else:
                        # if the next step is not a dict, then it is supposed to be the "tool" line
                        str_wrapper_name = self.__dict_workflow_definition[rule][key_second_step]
                # Instantiate the refered class and add it to the set of objects
                wrapper_entry = self.create_toolwrapper_entry(str_rule_name, str_wrapper_name, dict_dict_elm, input_entry, output_entry)
                wrapper_entry.execution = execution
                set_wrapper.add(wrapper_entry)
                Logger.instance().debug("Object toolwrapper: " + str_wrapper_name + " created.")
            session.add_all(set_wrapper)
            # save all operations done so far.
            session.commit()
        except NoResultFound as e:
            session.rollback()
            raise WopMarsException("Error while parsing the configuration file. The database has not been setUp Correctly.",
                                   str(e))
        # except Exception as e:
        #     session.rollback()
        #     raise WopMarsException("Error while parsing the configuration file.", str(e))

    def create_toolwrapper_entry(self, str_rule_name, str_wrapper_name, dict_dict_elm, input_entry, output_entry):
        """
        Actual creating of the toolwrapper object.

        Str_rule_name is the String containing the name of the rule in which the toolwrapper will be used.
        Str_wrapper_name is the String containing the name of the toolwrapper. It will be used for importing the correct
        module and then for creating the class.
        Dict_dict_elm is the dict of dict of "input"s "output"s and "params" and will be used to make relations between
        options / input / output and the toolwrapper.

        The toolwrapper object is an entry of the table rule in the resulting database.

        If the scopêd_session has current modification, they probably will be commited during this method:
        tables are created and this can only be done with clean session.

        :param str_rule_name: String
        :param str_wrapper_name: String
        :param dict_dict_elm: Dict <String: Dict <String: String>>

        :return: TooLWrapper instance
        """
        session = SQLManager.instance().get_session()
        # Importing the module in the mod variable
        try:
            mod = importlib.import_module(str_wrapper_name)
            # Building the class object
            toolwrapper_class = eval("mod." + str_wrapper_name)
        except AttributeError:
            raise WopMarsException("Error while parsing the configuration file: \n\t",
                                   "The class " + str_wrapper_name + " doesn't exist.")
        except ImportError:
            raise WopMarsException("Error while parsing the configuration file:",
                                   str_wrapper_name + " module is not in the pythonpath.")
        # Initialize the instance of ToolWrapper
        toolwrapper_wrapper = toolwrapper_class(rule_name=str_rule_name)

        # associating ToolWrapper instances with their files / tables
        for input_f in dict_dict_elm["dict_input"]:
            dict_dict_elm["dict_input"][input_f].type = input_entry
            toolwrapper_wrapper.files.append(dict_dict_elm["dict_input"][input_f])

        for output_f in dict_dict_elm["dict_output"]:
            dict_dict_elm["dict_output"][output_f].type = output_entry
            toolwrapper_wrapper.files.append(dict_dict_elm["dict_output"][output_f])

        for opt in dict_dict_elm["dict_params"]:
            toolwrapper_wrapper.options.append(dict_dict_elm["dict_params"][opt])

        for input_t in toolwrapper_wrapper.get_input_table():
            # this is a preventing commit because next statement will create a new table and the session has to be clean
            session.commit()
            # the user-side tables are created during the reading of the definition file
            table_entry = IODbPut(name=input_t)

            # The table modification_table track the modifications on the user-side tables
            # todo ask lionel trigerring?
            modification_table_entry, created = session.get_or_create(ModificationTable,
                                                                      defaults={
                                                                          "date": datetime.datetime.fromtimestamp(
                                                                              time.time())},
                                                                      table_name=input_t)
            table_entry.type = input_entry
            table_entry.modification = modification_table_entry
            toolwrapper_wrapper.tables.append(table_entry)

        for output_t in toolwrapper_wrapper.get_output_table():
            session.commit()
            table_entry = IODbPut(name=output_t)
            modification_table_entry, created = session.get_or_create(ModificationTable,
                                                                      defaults={
                                                                          "date": datetime.datetime.fromtimestamp(
                                                                              time.time())},
                                                                      table_name=output_t
                                                                      )
            table_entry.type = output_entry
            table_entry.modification = modification_table_entry
            toolwrapper_wrapper.tables.append(table_entry)

        # the toolwrapper returned by this method are valid according to the toolwrapper developper
        toolwrapper_wrapper.is_content_respected()
        return toolwrapper_wrapper

    def is_grammar_respected(self):
        """
        Check if the definition file respects the grammar. Throw an exception if not.

        The grammar is the following:

        NEWLINE configfile
        WoPMaRS = rule
        rule       = "rule" (identifier | "") ":" ruleparams
        ni         = NEWLINE INDENT
        ruleparams = [ni tool] [ni input] [ni output] [ni params]
        NEWLINE WoPMaRS
        tool       = "tool"   ":"  identifier ”:” stringliteral
        input      = "input"  ":" (identifier ”:” stringliteral ni?)+
        output     = "output" ":" (identifier ”:” stringliteral ni?)+
        params     = "params" ":" (identifier ”:” stringliteral ni?)+

        :raise: WopMarsParsingException
        :return: void
        """
        exemple_file_def = """
    rule RULENAME:
        tool: TOOLNAME
        input:
            INPUTNAME: INPUTVALUE
        output:
            OUTPUTNAME: OUTPUTVALUE
        params:
            OPTIONNAME: OPTIONVALUE

    rule ...etc...
        """
        # recognize the rule blocks
        regex_step1 = re.compile(r"(^rule [^\s]+$)")

        # recognize the elements of the rule
        regex_step2 = re.compile(r"(^params$)|(^tool$)|(^input$)|(^output$)")

        # todo regex sur les "identifier : stringliteral"? verifier qu'ils respectent bien toutes les specs
        #  (-> utilisé en base de donnée)
        # The found words are tested against the regex to see if they match or not
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


                # todo ask lionel -> pour les classes métier: le dev doit créer un package et doit l'installer avant de pouvoir s'en servir
                # aitor aimerait regrouper des tw dans un package:
                #        snp.BedIntersect
                #        snp.MatrixScan
                #        snp.etc.
                if s_key_step2 == "tool":
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
