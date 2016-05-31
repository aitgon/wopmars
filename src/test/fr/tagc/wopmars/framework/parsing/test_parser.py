import os
import unittest
from unittest import TestCase

from fr.tagc.wopmars.framework.management.DAG import DAG
from fr.tagc.wopmars.framework.parsing.Parser import Parser
from fr.tagc.wopmars.framework.rule.IOFilePut import IOFilePut
from fr.tagc.wopmars.toolwrappers.FooWrapper4 import FooWrapper4
from fr.tagc.wopmars.toolwrappers.FooWrapper5 import FooWrapper5
from fr.tagc.wopmars.toolwrappers.FooWrapper6 import FooWrapper6
from fr.tagc.wopmars.utils.PathFinder import PathFinder
from fr.tagc.wopmars.utils.SetUtils import SetUtils


class TestParser(TestCase):
    def setUp(self):
        s_root_path = PathFinder.find_src(os.path.dirname(os.path.realpath(__file__)))

        # The good -------------------------------:

        self.__f_example_definition_file = open(s_root_path + "resources/example_def_file2.yml")
        try:
            self.__parser_right = Parser(self.__f_example_definition_file)
        except:
            raise AssertionError('Should not raise exception')

        # The ugly (malformed file) ----------------------------:

        self.__f_wrong_example_definition_file_malformed = open(s_root_path + "resources/example_def_file_wrong_yaml.yml")
        with self.assertRaises(SystemExit):
            Parser(self.__f_wrong_example_definition_file_malformed)

        # The bad (invalid file) -----------------------------------:
        self.__f_wrong_example_definition_file_invalid = open(s_root_path + "resources/example_def_file_wrong_content.yml")
        self.__parser_wrong = Parser(self.__f_wrong_example_definition_file_invalid)

    def tearDown(self):
        self.__f_example_definition_file.close()
        self.__f_wrong_example_definition_file_malformed.close()
        self.__f_wrong_example_definition_file_invalid.close()

    def test_parse(self):

        # The good --------------------------:
        set_toolwrappers = set()

        set_toolwrappers.add(FooWrapper4(input_file_dict={'input1': IOFilePut('input1', 'aFile.txt')},
                                         output_file_dict={'output1': IOFilePut('output1', 'aFile2.txt')},
                                         option_dict={}))

        set_toolwrappers.add(FooWrapper5(input_file_dict={'input1': IOFilePut('input1', 'aFile2.txt')},
                                         output_file_dict={'output1': IOFilePut('output1', 'aFile3.txt')},
                                         option_dict={}))

        set_toolwrappers.add(FooWrapper6(input_file_dict={'input1': IOFilePut('input1', 'aFile2.txt')},
                                         output_file_dict={'output1': IOFilePut('output1', 'aFile4.txt')},
                                         option_dict={}))

        dag_expected = DAG(set_toolwrappers)
        dag_obtained = self.__parser_right.parse()

        self.assertEqual(dag_expected, dag_obtained)

        # The bad --------------------------:
        with self.assertRaises(SystemExit):
            self.__parser_wrong.parse()



if __name__ == '__main__':
    unittest.main()