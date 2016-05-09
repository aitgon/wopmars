import unittest
import os
from unittest import TestCase
from src.main.fr.tagc.wopmars.framework.parsing.Reader import Reader
from src.main.fr.tagc.wopmars.framework.rule.ObjectSet import ObjectSet
from src.main.fr.tagc.wopmars.toolwrappers.FooWrapper1 import FooWrapper1
from src.main.fr.tagc.wopmars.toolwrappers.FooWrapper2 import FooWrapper2
from src.main.fr.tagc.wopmars.toolwrappers.FooWrapper3 import FooWrapper3
from src.main.fr.tagc.wopmars.utils.PathFinder import PathFinder
from src.main.fr.tagc.wopmars.utils.SetUtils import SetUtils
from src.main.fr.tagc.wopmars.utils.exceptions.ParsingException import ParsingException


class TestReader(TestCase):

    def setUp(self):
        s_root_path = PathFinder.find_src(os.path.dirname(os.path.realpath(__file__)))
        s_path_to_example_definition_file = s_root_path + "resources/example_def_file.yml"
        s_path_to_not_existing_example_definition_file = s_root_path + "definition_file_that_doesnt_exists.yml"
        s_path_to_wrong_example_definition_file1 = s_root_path + "resources/example_def_file_wrong_yaml.yml"
        s_path_to_wrong_example_definition_file2 = s_root_path + "resources/example_def_file_wrong_grammar.yml"
        s_path_to_wrong_example_definition_file3 = s_root_path + "resources/example_def_file_wrong_grammar2.yml"

        self.assertRaises(ParsingException, Reader, s_path_to_wrong_example_definition_file1)
        self.assertRaises(ParsingException, Reader, s_path_to_not_existing_example_definition_file)
        self.assertRaises(ParsingException, Reader, s_path_to_wrong_example_definition_file2)
        self.assertRaises(ParsingException, Reader, s_path_to_wrong_example_definition_file3)
        try:
            self.__my_reader = Reader(s_path_to_example_definition_file)
        except:
            raise AssertionError('Should not raise exception')

    def test_read(self):

        result = self.__my_reader.read()
        expected = ObjectSet(s_type="wrapper")

        set_input = ObjectSet(s_type="input", dicto={'AnOtherThing': 'the_second_file.txt'})
        set_params = ObjectSet(s_type="params", dicto={'-f': 10.285})
        set_output = ObjectSet(s_type="output", dicto={'Resultat': 'the final_file.txt'})
        expected.add(FooWrapper3(inputSet=set_input, outputSet=set_output, optionSet=set_params))

        set_input = ObjectSet(s_type="input", dicto={'Something': 'aFile.txt'})
        set_params = ObjectSet(s_type="params", dicto={'-t': 5})
        expected.add(FooWrapper1(inputSet=set_input, outputSet=None, optionSet=set_params))

        set_params = ObjectSet(s_type="params", dicto={'-o': 'an_option'})
        set_output = ObjectSet(s_type="output", dicto={'Resultat': 'the second file.txt'})
        expected.add(FooWrapper2(inputSet=None, outputSet=set_output, optionSet=set_params))

        self.assertTrue((SetUtils.all_elm_of_one_set_in_one_other(result, expected) and
                         SetUtils.all_elm_of_one_set_in_one_other(expected, result)))


if __name__ == "__main__":
    unittest.main()