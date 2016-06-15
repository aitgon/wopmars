import os
import unittest
from unittest import TestCase

from FooWrapper4 import FooWrapper4
from FooWrapper5 import FooWrapper5
from FooWrapper6 import FooWrapper6
from FooWrapper7 import FooWrapper7
from FooWrapper8 import FooWrapper8
from FooWrapper9 import FooWrapper9
from src.main.fr.tagc.wopmars.framework.bdd.SQLManager import SQLManager
from src.main.fr.tagc.wopmars.framework.bdd.tables.IODbPut import IODbPut
from src.main.fr.tagc.wopmars.framework.bdd.tables.IOFilePut import IOFilePut
from src.main.fr.tagc.wopmars.framework.bdd.tables.RuleFile import RuleFile
from src.main.fr.tagc.wopmars.framework.bdd.tables.RuleTable import RuleTable
from src.main.fr.tagc.wopmars.framework.bdd.tables.Type import Type
from src.main.fr.tagc.wopmars.framework.management.DAG import DAG
from src.main.fr.tagc.wopmars.framework.parsing.Parser import Parser
from src.main.fr.tagc.wopmars.utils.OptionManager import OptionManager
from src.main.fr.tagc.wopmars.utils.PathFinder import PathFinder
from src.main.fr.tagc.wopmars.utils.exceptions.WopMarsException import WopMarsException


class TestParser(TestCase):
    def setUp(self):
        OptionManager().initial_test_setup()

        SQLManager.instance().create_all()
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
        OptionManager()["--dot"] = None
        SQLManager.instance().drop_all()

    def test_parse(self):
        OptionManager().initial_test_setup()

        # The good --------------------------:
        set_toolwrappers = set()

        input_entry = Type(name="input")
        output_entry = Type(name="output")

        f1 = IOFilePut(name="input1", path="/home/giffon/Documents/wopmars/src/resources/input_File1.txt")
        f2 = IOFilePut(name="output1", path="/home/giffon/Documents/wopmars/src/resources/output_File1.txt")

        f3 = IOFilePut(name="input1", path="/home/giffon/Documents/wopmars/src/resources/output_File1.txt")

        f4 = IOFilePut(name="output1", path="/home/giffon/Documents/wopmars/src/resources/output_File2.txt")
        f5 = IOFilePut(name="output1", path="/home/giffon/Documents/wopmars/src/resources/output_File3.txt")
        f6 = IOFilePut(name="output2", path="/home/giffon/Documents/wopmars/src/resources/output_File4.txt")

        f7 = IOFilePut(name="input1", path="/home/giffon/Documents/wopmars/src/resources/output_File3.txt")
        f8 = IOFilePut(name="input2", path="/home/giffon/Documents/wopmars/src/resources/output_File2.txt")

        f9 = IOFilePut(name="output1", path="/home/giffon/Documents/wopmars/src/resources/output_File5.txt")

        f10 = IOFilePut(name="input1", path="/home/giffon/Documents/wopmars/src/resources/output_File4.txt")
        f11 = IOFilePut(name="output1", path="/home/giffon/Documents/wopmars/src/resources/output_File6.txt")

        rf1 = RuleFile()
        rf1.file = f1
        rf1.type = input_entry

        rf2 = RuleFile()
        rf2.file = f2
        rf2.type = output_entry

        rf3 = RuleFile()
        rf3.file = f3
        rf3.type = input_entry

        rf3bis = RuleFile()
        rf3bis.file = f3
        rf3bis.type = input_entry

        rf4 = RuleFile()
        rf4.file = f4
        rf4.type = output_entry

        rf5 = RuleFile()
        rf5.file = f5
        rf5.type = output_entry

        rf6 = RuleFile()
        rf6.file = f6
        rf6.type = output_entry

        rf7 = RuleFile()
        rf7.file = f7
        rf7.type = input_entry

        rf8 = RuleFile()
        rf8.file = f8
        rf8.type = input_entry

        rf9 = RuleFile()
        rf9.file = f9
        rf9.type = output_entry

        rf10 = RuleFile()
        rf10.file = f10
        rf10.type = input_entry

        rf11 = RuleFile()
        rf11.file = f11
        rf11.type = output_entry

        t1 = IODbPut(name="FooBase")
        t2 = IODbPut(name="FooBase2")

        rt1 = RuleTable()
        rt1.table = t1
        rt1.type = output_entry

        rt1bis = RuleTable()
        rt1bis.table = t1
        rt1bis.type = input_entry

        rt2 = RuleTable()
        rt2.table = t2
        rt2.type = output_entry

        rt2bis = RuleTable()
        rt2bis.table = t2
        rt2bis.type = input_entry

        tw1 = FooWrapper4(rule_name="rule1")
        tw1.files.extend([rf1, rf2])
        set_toolwrappers.add(tw1)
        tw2 = FooWrapper5(rule_name="rule2")
        tw2.files.extend([rf3, rf4])
        tw2.tables.extend([rt1])
        set_toolwrappers.add(tw2)
        tw3 = FooWrapper6(rule_name="rule3")
        tw3.files.extend([rf3bis, rf5, rf6])
        set_toolwrappers.add(tw3)
        tw4 = FooWrapper7(rule_name="rule4")
        tw4.tables.extend([rt1bis, rt2])
        set_toolwrappers.add(tw4)
        tw5 = FooWrapper8(rule_name="rule5")
        tw5.files.extend([rf8, rf7, rf9])
        set_toolwrappers.add(tw5)
        tw6 = FooWrapper9(rule_name="rule6")
        tw6.files.extend([rf10, rf11])
        tw6.tables.extend([rt2bis])
        set_toolwrappers.add(tw6)

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
        os.remove(self.__dot_path[:-4] + ".ps")

if __name__ == '__main__':
    unittest.main()
