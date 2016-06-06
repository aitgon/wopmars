"""
This module contains the Reader class
"""
import yaml
import importlib
import re

from src.main.fr.tagc.wopmars.utils.DictUtils import DictUtils
from src.main.fr.tagc.wopmars.framework.rule.IOFilePut import IOFilePut
from src.main.fr.tagc.wopmars.framework.rule.Option import Option
from src.main.fr.tagc.wopmars.utils.Logger import Logger
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

        The method is_grammar_respected is called and can raise WopMarsParsingException too.

        :raise: WopMarsParsingException: if the Yaml Spec are not respected
        :param: s_definition_file: String: the definition file open in read mode
        """
        # Tests about grammar and syntax are performed here (file's existence is also tested here)
        try:
            def_file = open(s_definition_file, 'r')
            try:
                # The workflow definition file is loaded as-it in memory by the pyyaml library
                Logger().info("Reading the definition file: " + str(s_definition_file) + "...")
                self.__dict_workflow_definition = yaml.load(def_file)
                Logger().debug("\n" + DictUtils.pretty_repr(self.__dict_workflow_definition))
                Logger().info("Read complete.")
                Logger().info("Checking whether the file is well formed...")
                self.is_grammar_respected()
                Logger().info("File well formed.")
            # YAMLError is thrown if the YAML specifications are not respected by the definition file
            except yaml.YAMLError as exc:
                raise WopMarsException("Error while parsing the configuration file: \n\t"
                                       "The YAML specification is not respected:", str(exc))
            finally:
                def_file.close()
        except FileNotFoundError:
            raise WopMarsException("Error while parsing the configuration file: \n\tInput error:",
                                   "The specified file at " + s_definition_file + " doesn't exist.")

    def read(self):
        """
        Reads the file and extract the set of ToolWrapper.

        The definition file is supposed to be properly formed. The validation of the content of the definition is done
        during the instanciation of the tools.

        :return: The set of builded ToolWrappers
        """
        set_wrapper = set()

        for rule in self.__dict_workflow_definition:
            # the name of the wrapper is extracted after the "rule" keyword
            str_wrapper_name = rule.split()[-1].strip(":")
            # The dict is re-initialized for each wrapper
            dict_dict_elm = dict(dict_input={}, dict_params={}, dict_output={})
            for key_second_step in self.__dict_workflow_definition[rule]:
                # key_second_step is supposed to be "input", "output" or "params"
                for elm in self.__dict_workflow_definition[rule][key_second_step]:
                    # The 2 possible objects can be created
                    if key_second_step == "params":
                        obj_created = Option(elm, self.__dict_workflow_definition[rule][key_second_step][elm])
                    else:
                        # In theory, there cannot be a IODbPut specification in the definition file
                        obj_created = IOFilePut(elm, self.__dict_workflow_definition[rule][key_second_step][elm])
                    dict_dict_elm["dict_" + key_second_step][elm] = obj_created
            try:
                # Importing the module in the mod variable
                mod = importlib.import_module(str_wrapper_name)
            except ImportError:
                raise WopMarsException("Error while parsing the configuration file:",
                                       str_wrapper_name + " module is not in the pythonpath.")
            # Instantiate the refered class and add it to the set of objects

            try:
                toolwrapper_wrapper = eval("mod." + str_wrapper_name)(input_file_dict=dict_dict_elm["dict_input"],
                                                                      output_file_dict=dict_dict_elm["dict_output"],
                                                                      option_dict=dict_dict_elm["dict_params"])
            except AttributeError:
                raise WopMarsException("Error while parsing the configuration file: \n\t",
                                       "The class " + str_wrapper_name + " doesn't exist.")
            toolwrapper_wrapper.is_content_respected()
            set_wrapper.add(toolwrapper_wrapper)
        return set_wrapper

    def is_grammar_respected(self):
        """
        Check if the definition file respects the grammar. Throw an exception if not.

        The grammar is the following:

        NEWLINE configfile
        WoPMaRS = rule
        rule       = "rule" (identifier | "") ":" ruleparams
        ni         = NEWLINE INDENT
        ruleparams = [ni input] [ni output] [ni params]
        NEWLINE WoPMaRS
        input      = "input" ":" ((identifier ”:” stringliteral),?)+
        output     = "output" ":" ((identifier ”:” stringliteral),?)+
        params     = "params" ":" ((identifier ”:” stringliteral),?)+

        :raise: WopMarsParsingException
        :return: void
        """
        regex_step1 = re.compile(r"(^rule [^\s]+$)")
        regex_step2 = re.compile(r"(^params$)|(^input$)|(^output$)")

        # The found words are tested against the regex to see if they match or not
        for s_key_step1 in self.__dict_workflow_definition:
            if not regex_step1.search(s_key_step1):
                raise WopMarsException("Error while parsing the configuration file: \n\t"
                                       "The grammar of the WopMars's definition file is not respected:",
                                       "The line containing:\'" +
                                       str(s_key_step1) +
                                       "\' doesn't match the grammar: it should start with 'rule'" +
                                       "and contains only one word after the 'rule' keyword")
            for s_key_step2 in self.__dict_workflow_definition[s_key_step1]:
                if not regex_step2.search(s_key_step2):
                    raise WopMarsException("Error while parsing the configuration file: \n\t"
                                           "The grammar of the WopMars's definition file is not respected:",
                                           "The line containing:\'" + str(s_key_step2) +
                                           "\' doesn't match the grammar: it should be " +
                                           "'params', 'input' or 'output'")
