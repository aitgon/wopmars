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

        The method is_grammar_respected is called and can raise WopMarsParsingException too.

        :raise: WopMarsParsingException: if the Yaml Spec are not respected
        :param: s_definition_file: String: the definition file open in read mode
        """
        # Tests about grammar and syntax are performed here (file's existence is also tested here)
        try:
            def_file = open(s_definition_file, 'r')
            try:
                # The workflow definition file is loaded as-it in memory by the pyyaml library
                Logger.instance().info("Reading the definition file: " + str(s_definition_file) + "...")
                self.__dict_workflow_definition = yaml.load(def_file)
                Logger.instance().debug("\n" + DictUtils.pretty_repr(self.__dict_workflow_definition))
                Logger.instance().info("Read complete.")
                Logger.instance().info("Checking whether the file is well formed...")
                self.is_grammar_respected()
                Logger.instance().info("File well formed.")
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
        Logger.instance().debug("Parsing rules: " + str(self.__dict_workflow_definition))
        for rule in self.__dict_workflow_definition:
            str_wrapper_name = None
            # the name of the wrapper is extracted after the "rule" keyword
            str_rule_name = rule.split()[-1].strip(":")
            # The dict is re-initialized for each wrapper
            dict_dict_elm = dict(dict_input={}, dict_params={}, dict_output={})
            for key_second_step in self.__dict_workflow_definition[rule]:
                # key_second_step is supposed to be "tool", "input", "output" or "params"
                if type(self.__dict_workflow_definition[rule][key_second_step]) == dict:
                    for elm in self.__dict_workflow_definition[rule][key_second_step]:
                        # The 2 possible objects can be created
                        if key_second_step == "params":
                            obj_created = Option(elm, self.__dict_workflow_definition[rule][key_second_step][elm])
                        else:
                            # In theory, there cannot be a IODbPut specification in the definition file
                            obj_created = IOFilePut(elm, self.__dict_workflow_definition[rule][key_second_step][elm])
                        dict_dict_elm["dict_" + key_second_step][elm] = obj_created
                else:
                    str_wrapper_name = self.__dict_workflow_definition[rule][key_second_step]


            Logger.instance().debug("Loading " + str_wrapper_name + ".")
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
                Logger.instance().debug(str_wrapper_name + " ToolWrapper loaded.")
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

        regex_step1 = re.compile(r"(^rule [^\s]+$)")
        regex_step2 = re.compile(r"(^params$)|(^tool$)|(^input$)|(^output$)")

        # todo regex sur les "identifier : stringliteral"?
        # The found words are tested against the regex to see if they match or not
        for s_key_step1 in self.__dict_workflow_definition:
            bool_toolwrapper = False
            if not regex_step1.search(s_key_step1):
                raise WopMarsException("Error while parsing the configuration file: \n\t"
                                       "The grammar of the WopMars's definition file is not respected:",
                                       "The line containing:\'" +
                                       str(s_key_step1) +
                                       "\' doesn't match the grammar: it should start with 'rule'" +
                                       "and contains only one word after the 'rule' keyword" +
                                       "\nexemple:" + exemple_file_def)
            for s_key_step2 in self.__dict_workflow_definition[s_key_step1]:
                if not regex_step2.search(s_key_step2):
                    raise WopMarsException("Error while parsing the configuration file: \n\t"
                                           "The grammar of the WopMars's definition file is not respected:",
                                           "The line containing:'" + str(s_key_step2) + "'" +
                                           " for rule '" + str(s_key_step1) + "'" +
                                           " doesn't match the grammar: it should be " +
                                           "'tool', 'params', 'input' or 'output'" +
                                       "\nexemple:" + exemple_file_def)
                if s_key_step2 == "tool":
                    bool_toolwrapper = True

            if not bool_toolwrapper:
                raise WopMarsException("Error while parsing the configuration file: \n\t"
                                       "The grammar of the WopMars's definition file is not respected:",
                                       "The rule '" + str(s_key_step1) + "' doesn't contain any tool." +
                                       "\nexemple:" + exemple_file_def
                                       )

if __name__ == '__main__':
    OptionManager()["-v"] = 3
    try:
        r = Reader("/home/giffon/Documents/wopmars/src/resources/example_def_file.yml")
    except Exception as e:
        print(e)