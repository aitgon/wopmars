"""
This module contains the Reader class
"""
import yaml
import importlib
import re

from fr.tagc.wopmars.framework.rule.IOFilePut import IOFilePut
from fr.tagc.wopmars.framework.rule.Option import Option
from fr.tagc.wopmars.utils.exceptions.WopMarsParsingException import WopMarsParsingException


class Reader:
    """
    The reader class is used to read the workflow definition file,
    build the ToolWrapper objects and perform tests on the quality
    of the definition file.
    """
    def __init__(self, f_definition_file):
        """
        Constructor of the reader which also test the feasability of the read

        :param f_definition_file_path: file: the definition file open in read mode
        """
        # todo ask lionel faire passer le fichier plutot que la string, maintenant qu'ile st ouvert...
        # self.__s_definition_file_path = s_definition_file_path

        # Tests about grammar and syntax are performed here (file's existence is also tested here)
        # todo enlever tous ces morceaux de code commentés
        # try:
        #todo loging
        print("Reading the definition file: " + str(f_definition_file.name) + "...", end="")
        # def_file = open(self.__s_definition_file_path, 'r')

        try:
            # The workflow definition file is loaded as-it in memory by the pyyaml library
            # self.__dict_workflow_definition = yaml.load(def_file)
            self.__dict_workflow_definition = yaml.load(f_definition_file)
            # todo loging
            print(" -> done.")
            # todo loging
            print("Checking whether the file is well formed...", end="")
            self.is_grammar_respected()
            # todo loging
            print(" -> done.\n")
        # YAMLError is thrown if the YAML specifications are not respected by the definition file
        except yaml.YAMLError as exc:
            print()
            raise WopMarsParsingException(1, str(exc))
            # finally:
            #     def_file.close()
        # except FileNotFoundError:
        #     raise WopMarsParsingException(0, "The specified file at " +
        #                                   self.__s_definition_file_path + " doesn't exist.")

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
            # TODO ask lionel factory pour faire ça? - Vérifier avec Lionel et Aïtor comment on va gérer les classes wrappers
            # au nvieau de l'arborescence des fichiers.


            # todo try except pour vérifier que la classe wrapper existe
            try:
                # Importing the module in the mod variable
                mod = importlib.import_module("fr.tagc.wopmars.toolwrappers." + str_wrapper_name)
            except ImportError:
                print()
                raise WopMarsParsingException(5, str_wrapper_name + " module is not in the pythonpath.")
            # Instantiate the refered class and add it to the set of objects

            try:
                toolwrapper_wrapper = eval("mod." + str_wrapper_name)(input_file_dict=dict_dict_elm["dict_input"],
                                                                      output_file_dict=dict_dict_elm["dict_output"],
                                                                      option_dict=dict_dict_elm["dict_params"])
            except AttributeError:
                print()
                raise WopMarsParsingException(5, "The class " + str_wrapper_name + " doesn't exist.")
            toolwrapper_wrapper.is_content_respected()
            set_wrapper.add(toolwrapper_wrapper)
        return set_wrapper

    def is_grammar_respected(self):
        """
        Check if the definition file respects the grammar. Throw an exception if not.

        :return: void
        """
        regex_step1 = re.compile(r"(^rule [^\s]+$)")
        regex_step2 = re.compile(r"(^params$)|(^input$)|(^output$)")

        # The found words are tested against the regex to see if they match or not
        for s_key_step1 in self.__dict_workflow_definition:
            if not regex_step1.search(s_key_step1):
                raise WopMarsParsingException(2, "The line containing:\'" +
                                              str(s_key_step1) +
                                              "\' doesn't match the grammar: it should start with 'rule'" +
                                              "and contains only one word after the 'rule' keyword")
            for s_key_step2 in self.__dict_workflow_definition[s_key_step1]:
                if not regex_step2.search(s_key_step2):
                    raise WopMarsParsingException(2, "The line containing:\'" + str(s_key_step2) +
                                                  "\' doesn't match the grammar: it should be " +
                                                  "'params', 'input' or 'output'")

if __name__ == "__main__":
    my_reader = Reader("/home/giffon/Documents/wopmars/src/resources/example_def_file.yml")
    set_toolwrappers = my_reader.read()