import os
import unittest
from unittest import TestCase

from fr.tagc.wopmars.framework.management.DAG import DAG
from fr.tagc.wopmars.framework.parsing.Parser import Parser
from fr.tagc.wopmars.framework.rule.IOFilePut import IOFilePut
from fr.tagc.wopmars.toolwrappers.FooWrapper4 import FooWrapper4
from fr.tagc.wopmars.toolwrappers.FooWrapper5 import FooWrapper5
from fr.tagc.wopmars.toolwrappers.FooWrapper6 import FooWrapper6
from fr.tagc.wopmars.utils.OptionManager import OptionManager
from fr.tagc.wopmars.utils.PathFinder import PathFinder
from fr.tagc.wopmars.utils.exceptions.WopMarsException import WopMarsException


class TestParser(TestCase):
    def setUp(self):
        OptionManager({'-v': 1, "--dot": None})
        s_root_path = PathFinder.find_src(os.path.dirname(os.path.realpath(__file__)))

        # The good -------------------------------:

        s_example_definition_file = s_root_path + "resources/example_def_file2.yml"
        self.__parser_right = Parser(s_example_definition_file)

        # The bad (invalid file) -----------------------------------:
        s_wrong_example_definition_file_invalid = s_root_path + "resources/example_def_file_not_a_dag.yml"
        self.__parser_wrong = Parser(s_wrong_example_definition_file_invalid)

        # Dot path --------------:

        self.__dot_path = s_root_path + "test.dot"

    def tearDown(self):
        OptionManager()["--dot"] = None 

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

        OptionManager()["--dot"] = None

        dag_expected = DAG(set_toolwrappers)
        dag_obtained = self.__parser_right.parse()

        self.assertEqual(dag_expected, dag_obtained)

        # The bad --------------------------:
        with self.assertRaises(WopMarsException):
            self.__parser_wrong.parse()

        # Verify the dot file ----------------:

        OptionManager()["--dot"] = self.__dot_path
        self.__parser_right.parse()
        self.assertTrue(os.path.isfile(self.__dot_path))
        os.remove(self.__dot_path)

if __name__ == '__main__':
    unittest.main()
