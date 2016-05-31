import unittest
import os
from unittest import TestCase
from fr.tagc.wopmars.framework.parsing.Reader import Reader
from fr.tagc.wopmars.framework.rule.IOFilePut import IOFilePut
from fr.tagc.wopmars.framework.rule.Option import Option
from fr.tagc.wopmars.toolwrappers.FooWrapper1 import FooWrapper1
from fr.tagc.wopmars.toolwrappers.FooWrapper2 import FooWrapper2
from fr.tagc.wopmars.toolwrappers.FooWrapper3 import FooWrapper3
from fr.tagc.wopmars.utils.PathFinder import PathFinder
from fr.tagc.wopmars.utils.SetUtils import SetUtils
from fr.tagc.wopmars.utils.exceptions.WopMarsParsingException import WopMarsParsingException


class TestReader(TestCase):

    def setUp(self):
        s_root_path = PathFinder.find_src(os.path.dirname(os.path.realpath(__file__)))

        # The good -------------------------------:

        self.__f_example_definition_file = open(s_root_path + "resources/example_def_file.yml")
        try:
            self.__reader_right = Reader(self.__f_example_definition_file)
        except:
            raise AssertionError('Should not raise exception')

        # The ugly (malformed file) --------------------:

        self.__list_f_to_exception_init = [
            open(s_root_path + s_path) for s_path in [
                "resources/example_def_file_wrong_yaml.yml",
                "resources/example_def_file_wrong_grammar.yml",
                "resources/example_def_file_wrong_grammar2.yml",
                ]
        ]

        [self.assertRaises(WopMarsParsingException, Reader, file) for file in self.__list_f_to_exception_init]

        # The bad (invalid file) ----------------------:

        self.__list_f_to_exception_read = [
            open(s_root_path + s_path) for s_path in [
                "resources/example_def_file_wrong_content.yml",
                "resources/example_def_file_wrong_content2.yml",
                "resources/example_def_file_wrong_content3.yml",
                "resources/example_def_file_wrong_content4.yml",
                "resources/example_def_file_wrong_content5.yml",
                "resources/example_def_file_wrong_class_name.yml",
                "resources/example_def_file_wrong_rule.yml",
            ]
        ]

        self.__list_reader_exception_read = [Reader(file) for file in self.__list_f_to_exception_read]

    def tearDown(self):
        self.__f_example_definition_file.close()
        [f.close() for f in self.__list_f_to_exception_init]
        [f.close() for f in self.__list_f_to_exception_read]

    def test_read(self):

        result = self.__reader_right.read()

        expected = set()

        expected.add(FooWrapper3(input_file_dict={'input1': IOFilePut('input1', 'the_second_file.txt')},
                                 output_file_dict={'output1': IOFilePut('output1', 'the final_file.txt')},
                                 option_dict={'param1': Option('param1', 10.285)}))

        expected.add(FooWrapper1(input_file_dict={'input1': IOFilePut('input1', 'aFile.txt')},
                                 output_file_dict={},
                                 option_dict={'param1': Option('param1', 5)}))

        expected.add(FooWrapper2(input_file_dict={},
                                 output_file_dict={'output1': IOFilePut('output1', 'the second file.txt')},
                                 option_dict={'param1': Option('param1', 'an_option')}))

        # The good ------------------------------------:

        self.assertTrue((SetUtils.all_elm_of_one_set_in_one_other(result, expected) and
                         SetUtils.all_elm_of_one_set_in_one_other(expected, result)))

        # The bad -------------------------------------:

        [self.assertRaises(WopMarsParsingException, reader.read) for reader in self.__list_reader_exception_read]


if __name__ == "__main__":
    unittest.main()