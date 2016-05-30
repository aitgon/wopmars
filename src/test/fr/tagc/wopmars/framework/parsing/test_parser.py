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

        s_path_to_example_definition_file = s_root_path + "resources/example_def_file2.yml"
        s_path_to_not_existing_example_definition_file = s_root_path + "definition_file_that_doesnt_exists.yml"
        s_path_to_wrong_example_definition_file1 = s_root_path + "resources/example_def_file_wrong_content.yml"
        s_path_to_wrong_example_definition_file_not_dag = s_root_path + "resources/example_def_file_not_a_dag.yml"

        self.__parser_right = Parser(s_path_to_example_definition_file)
        self.__parser_wrong = Parser(s_path_to_wrong_example_definition_file1)
        self.__parser_wrong_not_dag = Parser(s_path_to_wrong_example_definition_file_not_dag)
        with self.assertRaises(SystemExit):
            Parser(s_path_to_not_existing_example_definition_file)

    def test_parse(self):
        with self.assertRaises(SystemExit):
            self.__parser_wrong.parse()

        with self.assertRaises(SystemExit):
            self.__parser_wrong_not_dag.parse()

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

        int_nodes_expected = len(dag_expected.nodes())
        int_nodes_obtained = len(dag_obtained.nodes())

        set_edges_expected = set(dag_expected.edges())
        set_edges_obtained = set(dag_obtained.edges())

        self.assertEqual(int_nodes_expected, int_nodes_obtained)
        self.assertTrue(SetUtils.all_elm_of_one_set_in_one_other(set_edges_expected, set_edges_obtained))
        self.assertTrue(SetUtils.all_elm_of_one_set_in_one_other(set_edges_obtained, set_edges_expected))

if __name__ == '__main__':
    unittest.main()