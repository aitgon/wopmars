"""
This module contains the Reader class
"""
import yaml
import importlib
import re

from src.main.fr.tagc.wopmars.framework.rule.ObjectSet import ObjectSet
from src.main.fr.tagc.wopmars.utils.exceptions.ParsingException import ParsingException


class Reader:
    """
    The reader class is used to read the workflow definition file,
    build the ToolWrapper objects and perform tests on the quality
    of the definition file.
    """    
    def __init__(self, s_definition_file_path):
        """
        Constructor of the reader which also test the feasability of the read

        :param s_definition_file_name: String: the Path to the definition file
        """
        self.__s_definition_file_path = s_definition_file_path

        try:
            # The workflow definition file is loaded as-it in memory by the pyyaml library
            def_file = open(self.__s_definition_file_path, 'r')
            try:
                self.__dict_workflow_definition = yaml.load(def_file)
                # TODO ask Lionel if the multiple parsing of the dict is a problem
                self.is_grammar_respected()
                self.is_content_respected()
            # check the yaml syntax
            except yaml.YAMLError as exc:
                # TODO ask Lionel if that exception is properly chosen
                #   should i create more exceptions more specific and make the parser throws "parsing exception" which
                #   should be caught in the main?
                raise ParsingException(str(exc))
            finally:
                def_file.close()
        except FileNotFoundError:
            raise ParsingException("The specified file at " + self.__s_definition_file_path + " doesn't exist.")

    def read(self):
        """
        Reads the file and extract the set of ToolWrapper. The definition file is supposed to be properly formed.

        :return: The set of builded ToolWrappers in an ObjectSet object
        """
        # Tests about grammar and syntax are performed here (file's existence is also tested here)

        set_wrapper = ObjectSet(s_type="wrapper")

        for rule in self.__dict_workflow_definition:
            str_wrapper_name = rule.split()[-1].strip(":")
            # Importing the module in the mod variable
            dict_object_set = dict(set_input=None, set_params=None, set_output=None)

            for key_second_step in self.__dict_workflow_definition[rule]:
                dict_object_set["set_" + key_second_step] = ObjectSet(s_type=key_second_step, dicto=self.__dict_workflow_definition[rule][key_second_step])

            mod = importlib.import_module("src.main.fr.tagc.wopmars.toolwrappers." + str_wrapper_name)
            # Instantiate the refered class and add it to the set of objects
            set_wrapper.add(eval("mod." + str_wrapper_name)(inputSet=dict_object_set["set_input"],
                                                            outputSet=dict_object_set["set_output"],
                                                            optionSet=dict_object_set["set_params"]))

        return set_wrapper

    def is_grammar_respected(self):
        """
        Check if the definition file respects the grammar. Throw an exception if not.

        :return: void
        """
        regex_step1 = re.compile("(^rule )")
        regex_step2 = re.compile("(^params$)|(^input$)|(^output$)")

        for s_key_step1 in self.__dict_workflow_definition:
            if not regex_step1.search(s_key_step1):
                raise ParsingException("The line containing :\'" +
                                       str(s_key_step1) +
                                       "\' doesn't match the grammar: it should be 'rule'")
            for s_key_step2 in self.__dict_workflow_definition[s_key_step1]:
                if not regex_step2.search(s_key_step2):
                    raise ParsingException("The line containing :\'" + str(s_key_step2) +
                                           "\' doesn't match the grammar: " +
                                           "it should start with 'params', " +
                                           "'input' or 'output'")

    def is_content_respected(self):
        """
        Check if the definition file respects the name rules given by the wrapper developper.  Throw an exception if not

        :return: void
        """
        for s_key_step1 in self.__dict_workflow_definition:
            str_wrapper_name = s_key_step1.split()[-1].strip(":")
            mod = importlib.import_module("src.main.fr.tagc.wopmars.toolwrappers." + str_wrapper_name)
            # TODO verifier que les tools existent: voir avec lionel comment les outils doivent être développés

            # the folowing blocks of code are VERY dirty
            # i have to find a way to make it better
            # TODO refactor this code  ->

            # Check if the input variables are ok
            list_input_file = eval("mod." + str_wrapper_name).get_input_file()
            # Build a regex from the list given by the tool's get method
            regex_input = re.compile("(^{0}$)".format('$)|(^'.join(list_input_file)))
            for s_input in self.__dict_workflow_definition[s_key_step1]["input"]:
                if not regex_input.search(s_input):
                    raise ParsingException("The line containing :\'" +
                                           str(s_input) +
                                           "\' doesn't match the grammar: it should be with " +
                                           "'{0}'".format("', '".join(list_input_file)))

            # Check if the output variables are ok
            list_output_file = eval("mod." + str_wrapper_name).get_output_file()
            # Build a regex from the list given by the tool's get method
            regex_output = re.compile("(^{0}$)".format('$)|(^'.join(list_output_file)))
            for s_output in self.__dict_workflow_definition[s_key_step1]["output"]:
                if not regex_output.search(s_output):
                    raise ParsingException("The line containing :\'" +
                                           str(s_output) +
                                           "\' doesn't match the grammar: it should be with " +
                                           "'{0}'".format("', '".join(list_output_file)))

            # Check if the output variables are ok
            dict_options = eval("mod." + str_wrapper_name).get_params()
            # Build a regex from the list given by the tool's get method
            regex_option = re.compile("(^{0}$)".format('$)|(^'.join(dict_options.keys())))
            for s_option in self.__dict_workflow_definition[s_key_step1]["params"]:
                if not regex_option.search(s_option):
                    raise ParsingException("The line containing :\'" +
                                           str(s_option) +
                                           "\' doesn't match the grammar: it should be with " +
                                           "'{0}'".format("', '".join(dict_options.keys())))
                # TODO check the type of the corresponding item

            # for s_key_step2 in self.__dict_workflow_definition[s_key_step1]:
        #         if not regex_step2.search(s_key_step2):
        #             raise ParsingException("The line containing :\'" + str(s_key_step2) +
        #                                    "\' doesn't match the grammar: " +
        #                                    "it should start with 'params', " +
        #                                    "'input' or 'output'")

if __name__ == "__main__":
    my_reader = Reader("/home/giffon/Documents/WopMars/projet/src/resources/example_def_file_wrong_content.yml")
    set_toolwrappers = my_reader.read()