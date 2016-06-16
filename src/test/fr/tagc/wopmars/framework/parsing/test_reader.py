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

from FooWrapper1 import FooWrapper1
from FooWrapper2 import FooWrapper2
from FooWrapper3 import FooWrapper3
from src.main.fr.tagc.wopmars.framework.bdd.tables.Option import Option
from src.main.fr.tagc.wopmars.framework.bdd.tables.RuleFile import RuleFile
from src.main.fr.tagc.wopmars.framework.bdd.tables.RuleTable import RuleTable
from src.main.fr.tagc.wopmars.framework.bdd.tables.ToolWrapper import ToolWrapper
from src.main.fr.tagc.wopmars.framework.bdd.tables.Type import Type
from src.main.fr.tagc.wopmars.framework.parsing.Reader import Reader
from src.main.fr.tagc.wopmars.utils.OptionManager import OptionManager
from src.main.fr.tagc.wopmars.utils.PathFinder import PathFinder
from src.main.fr.tagc.wopmars.utils.SetUtils import SetUtils
from src.main.fr.tagc.wopmars.utils.exceptions.WopMarsException import WopMarsException


class TestReader(TestCase):

    def setUp(self):
        OptionManager.initial_test_setup()
        SQLManager.instance().create_all()
        self.__session = SQLManager.instance().get_session()

        s_root_path = PathFinder.find_src(os.path.dirname(os.path.realpath(__file__)))

        # The good -------------------------------:

        self.__s_example_definition_file = s_root_path + "resources/example_def_file.yml"
        try:
            self.__reader_right = Reader(self.__s_example_definition_file)
        except:
            raise AssertionError('Should not raise exception')

        # The ugly (malformed file) --------------------:

        self.__s_example_definition_file_duplicate_rule = s_root_path + "resources/example_def_file_duplicate_rule.yml"

        self.__list_f_to_exception_init = [
            s_root_path + s_path for s_path in [
                "resources/example_def_file_wrong_yaml.yml",
                "resources/example_def_file_duplicate_rule.yml",
                "resources/example_def_file_wrong_grammar.yml",
                "resources/example_def_file_wrong_grammar2.yml",
                "resources/example_def_file_wrong_grammar3.yml",
                ]
        ]

        [self.assertRaises(WopMarsException, Reader, file) for file in self.__list_f_to_exception_init]

        # The bad (invalid file) ----------------------:

        self.__list_s_to_exception_read = [
            s_root_path + s_path for s_path in [
                "resources/example_def_file_wrong_content.yml",
                "resources/example_def_file_wrong_content2.yml",
                "resources/example_def_file_wrong_content3.yml",
                "resources/example_def_file_wrong_content4.yml",
                "resources/example_def_file_wrong_content5.yml",
                "resources/example_def_file_wrong_class_name.yml",
                "resources/example_def_file_wrong_rule.yml",
            ]
        ]

        self.__list_reader_exception_read = [Reader(file) for file in self.__list_s_to_exception_read]

        # Not existing file

        with self.assertRaises(WopMarsException):
            Reader(s_root_path + "Not existing file.")

    def tearDown(self):
        SQLManager.instance().drop_all()

    def test_check_duplicate_rule(self):
        with open(self.__s_example_definition_file_duplicate_rule) as file_duplicate_rule:
            with self.assertRaises(WopMarsException):
                Reader.check_duplicate_rules_and_check_from_opt(file_duplicate_rule.read())

    def test_read(self):

        self.__reader_right.read()
        result = set(self.__session.query(ToolWrapper).all())

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

        f12 = IOFilePut(name="input1", path="/home/giffon/Documents/wopmars/src/resources/output_File1.txt")
        f13 = IOFilePut(name="input2", path="/home/giffon/Documents/wopmars/src/resources/output_File5.txt")
        f14 = IOFilePut(name="input3", path="/home/giffon/Documents/wopmars/src/resources/output_File6.txt")
        f15 = IOFilePut(name="output1", path="/home/giffon/Documents/wopmars/src/resources/output_File7.txt")

        rf12 = RuleFile()
        rf12.file = f12
        rf12.type = input_entry

        rf13 = RuleFile()
        rf13.file = f13
        rf13.type = input_entry

        rf14 = RuleFile()
        rf14.file = f14
        rf14.type = input_entry

        rf15 = RuleFile()
        rf15.file = f15
        rf15.type = output_entry

        tw1 = FooWrapper4(rule_name="rule1")
        tw1.files.extend([rf1, rf2])
        tw2 = FooWrapper5(rule_name="rule2")
        tw2.files.extend([rf3, rf4])
        tw2.tables.extend([rt1])
        tw3 = FooWrapper6(rule_name="rule3")
        tw3.files.extend([rf3bis, rf5, rf6])
        tw4 = FooWrapper7(rule_name="rule4")
        tw4.tables.extend([rt1bis, rt2])
        tw5 = FooWrapper8(rule_name="rule5")
        tw5.files.extend([rf8, rf7, rf9])
        tw6 = FooWrapper9(rule_name="rule6")
        tw6.files.extend([rf10, rf11])
        tw6.tables.extend([rt2bis])
        tw7 = FooWrapper10(rule_name="rule7")
        tw7.files.extend([rf12, rf13, rf14, rf15])


        expected = set([tw1, tw2, tw3, tw4, tw5, tw6, tw7])


        # The good ------------------------------------:

        self.assertTrue((SetUtils.all_elm_of_one_set_in_one_other(result, expected) and
                         SetUtils.all_elm_of_one_set_in_one_other(expected, result)))

        # The bad -------------------------------------:

        [self.assertRaises(WopMarsException, reader.read) for reader in self.__list_reader_exception_read]


if __name__ == "__main__":
    unittest.main()