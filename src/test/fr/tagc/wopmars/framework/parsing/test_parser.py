import os
import unittest
from unittest import TestCase

from FooWrapper10 import FooWrapper10
from FooWrapper4 import FooWrapper4
from FooWrapper5 import FooWrapper5
from FooWrapper6 import FooWrapper6
from FooWrapper7 import FooWrapper7
from FooWrapper8 import FooWrapper8
from FooWrapper9 import FooWrapper9
from src.main.fr.tagc.wopmars.framework.bdd.SQLManager import SQLManager
from src.main.fr.tagc.wopmars.framework.bdd.tables.IODbPut import IODbPut
from src.main.fr.tagc.wopmars.framework.bdd.tables.IOFilePut import IOFilePut
from src.main.fr.tagc.wopmars.framework.bdd.tables.Type import Type
from src.main.fr.tagc.wopmars.framework.management.DAG import DAG
from src.main.fr.tagc.wopmars.framework.parsing.Parser import Parser
from src.main.fr.tagc.wopmars.utils.OptionManager import OptionManager
from src.main.fr.tagc.wopmars.utils.PathFinder import PathFinder
from src.main.fr.tagc.wopmars.utils.exceptions.WopMarsException import WopMarsException


class TestParser(TestCase):
    def setUp(self):
        OptionManager.initial_test_setup()

        SQLManager.create_all()
        s_root_path = PathFinder.find_src(os.path.dirname(os.path.realpath(__file__)))

        # The good -------------------------------:

        s_example_definition_file = s_root_path + "resources/example_def_file.yml"
        self.__parser_right = Parser(s_example_definition_file)

        # The bad (not a dag) -----------------------------------:
        s_wrong_example_definition_file_invalid = s_root_path + "resources/example_def_file_not_a_dag.yml"
        self.__parser_wrong = Parser(s_wrong_example_definition_file_invalid)

        # Dot path --------------:

        self.__dot_path = s_root_path + "test.dot"

    def tearDown(self):
        OptionManager.instance()["--dot"] = None
        SQLManager.drop_all()

    def test_parse(self):
        OptionManager.initial_test_setup()

        # The good --------------------------:
        input_entry = Type(name="input")
        output_entry = Type(name="output")

        f1 = IOFilePut(name="input1", path="/home/giffon/Documents/wopmars/src/resources/input_File1.txt")
        f1.type = input_entry

        f2 = IOFilePut(name="output1", path="/home/giffon/Documents/wopmars/src/resources/output_File1.txt")
        f2.type = output_entry

        f3 = IOFilePut(name="input1", path="/home/giffon/Documents/wopmars/src/resources/output_File1.txt")
        f3.type = input_entry

        f3bis = IOFilePut(name="input1", path="/home/giffon/Documents/wopmars/src/resources/output_File1.txt")
        f3bis.type = input_entry

        f4 = IOFilePut(name="output1", path="/home/giffon/Documents/wopmars/src/resources/output_File2.txt")
        f4.type = output_entry

        f5 = IOFilePut(name="output1", path="/home/giffon/Documents/wopmars/src/resources/output_File3.txt")
        f5.type = output_entry

        f6 = IOFilePut(name="output2", path="/home/giffon/Documents/wopmars/src/resources/output_File4.txt")
        f6.type = output_entry

        f7 = IOFilePut(name="input1", path="/home/giffon/Documents/wopmars/src/resources/output_File3.txt")
        f7.type = input_entry

        f8 = IOFilePut(name="input2", path="/home/giffon/Documents/wopmars/src/resources/output_File2.txt")
        f8.type = input_entry

        f9 = IOFilePut(name="output1", path="/home/giffon/Documents/wopmars/src/resources/output_File5.txt")
        f9.type = output_entry

        f10 = IOFilePut(name="input1", path="/home/giffon/Documents/wopmars/src/resources/output_File4.txt")
        f10.type = input_entry

        f11 = IOFilePut(name="output1", path="/home/giffon/Documents/wopmars/src/resources/output_File6.txt")
        f11.type = output_entry

        f12 = IOFilePut(name="input1", path="/home/giffon/Documents/wopmars/src/resources/output_File1.txt")
        f12.type = input_entry

        f13 = IOFilePut(name="input2", path="/home/giffon/Documents/wopmars/src/resources/output_File5.txt")
        f13.type = input_entry

        f14 = IOFilePut(name="input3", path="/home/giffon/Documents/wopmars/src/resources/output_File6.txt")
        f14.type = input_entry

        f15 = IOFilePut(name="output1", path="/home/giffon/Documents/wopmars/src/resources/output_File7.txt")
        f15.type = output_entry

        t1 = IODbPut(name="FooBase")
        t1.type = output_entry

        t1bis = IODbPut(name="FooBase")
        t1bis.type = input_entry

        t2 = IODbPut(name="FooBase2")
        t2.type = output_entry

        t2bis = IODbPut(name="FooBase2")
        t2bis.type = input_entry

        tw1 = FooWrapper4(rule_name="rule1")
        tw1.files.extend([f1, f2])
        tw2 = FooWrapper5(rule_name="rule2")
        tw2.files.extend([f3, f4])
        tw2.tables.extend([t1])
        tw3 = FooWrapper6(rule_name="rule3")
        tw3.files.extend([f3bis, f5, f6])
        tw4 = FooWrapper7(rule_name="rule4")
        tw4.tables.extend([t1bis, t2])
        tw5 = FooWrapper8(rule_name="rule5")
        tw5.files.extend([f8, f7, f9])
        tw6 = FooWrapper9(rule_name="rule6")
        tw6.files.extend([f10, f11])
        tw6.tables.extend([t2bis])
        tw7 = FooWrapper10(rule_name="rule7")
        tw7.files.extend([f12, f13, f14, f15])

        set_toolwrappers = set([tw1, tw2, tw3, tw4, tw5, tw6, tw7])

        OptionManager.instance()["--dot"] = None

        dag_expected = DAG(set_toolwrappers)
        dag_obtained = self.__parser_right.parse()

        self.assertEqual(dag_expected, dag_obtained)

        # The bad --------------------------:
        with self.assertRaises(WopMarsException):
            self.__parser_wrong.parse()

        # Verify the dot file ----------------:

        OptionManager.instance()["--dot"] = self.__dot_path
        self.__parser_right.parse()
        self.assertTrue(os.path.isfile(self.__dot_path))
        os.remove(self.__dot_path)
        os.remove(self.__dot_path[:-4] + ".ps")

if __name__ == '__main__':
    unittest.main()
