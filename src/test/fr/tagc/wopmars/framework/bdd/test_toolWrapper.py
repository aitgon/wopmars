import os
import unittest
from unittest import TestCase

from FooWrapper1 import FooWrapper1
from FooWrapper2 import FooWrapper2
from src.main.fr.tagc.wopmars.framework.bdd.SQLManager import SQLManager
from src.main.fr.tagc.wopmars.framework.bdd.tables.IODbPut import IODbPut
from src.main.fr.tagc.wopmars.framework.bdd.tables.IOFilePut import IOFilePut
from src.main.fr.tagc.wopmars.framework.bdd.tables.RuleFile import RuleFile
from src.main.fr.tagc.wopmars.framework.bdd.tables.RuleTable import RuleTable
from src.main.fr.tagc.wopmars.framework.bdd.tables.ToolWrapper import ToolWrapper

from FooWrapper8 import FooWrapper8
from FooWrapperNoTable import FooWrapperNoTable
from src.main.fr.tagc.wopmars.framework.bdd.tables.Option import Option
from src.main.fr.tagc.wopmars.framework.bdd.tables.Type import Type
from src.main.fr.tagc.wopmars.utils.OptionManager import OptionManager
from src.main.fr.tagc.wopmars.utils.PathFinder import PathFinder
from src.main.fr.tagc.wopmars.utils.exceptions.WopMarsException import WopMarsException
from src.test.fr.tagc.wopmars.toolwrappers.FooWrapper3 import FooWrapper3


class TestToolWrapper(TestCase):
    def setUp(self):
        OptionManager.initial_test_setup()

        set_tw_to_add = set()
        self.__session = SQLManager.instance().get_session()

        input_entry = Type(name="input")
        output_entry = Type(name="output")

        f1 = IOFilePut(name="input1", path="file1.txt")
        f2 = IOFilePut(name="output1", path="file2.txt")
        f3 = IOFilePut(name="input2", path="file2.txt")

        t1 = IODbPut(name="FooBase")
        t2 = IODbPut(name="FooBase")

        ### Toolwrappers for __eq__ test

        opt1 = Option(name="param1", value="1")
        opt2 = Option(name="param2", value="2")
        opt3 = Option(name="param1", value="String")

        rf1 = RuleFile()
        rf1.type = input_entry
        rf1.file = f1

        rf2 = RuleFile()
        rf2.type = output_entry
        rf2.file = f2

        self.__toolwrapper1 = ToolWrapper(rule_name="rule1")
        self.__toolwrapper1.files.extend([rf1, rf2])
        self.__toolwrapper1.options.append(opt1)

        rf1 = RuleFile()
        rf1.type = input_entry
        rf1.file = f1

        rf2 = RuleFile()
        rf2.type = output_entry
        rf2.file = f2

        self.__toolwrapper2 = ToolWrapper(rule_name="rule2")
        self.__toolwrapper2.files.extend([rf1, rf2])
        self.__toolwrapper2.options.append(opt1)

        rf1 = RuleFile()
        rf1.type = input_entry
        rf1.file = f1

        rf2 = RuleFile()
        rf2.type = output_entry
        rf2.file = f2

        self.__toolwrapper3 = ToolWrapper(rule_name="rule3")
        self.__toolwrapper3.files.extend([rf1, rf2])
        self.__toolwrapper3.options.append(opt2)

        ### ToolWrappers for content_respected

        rf1 = RuleFile()
        rf1.type = input_entry
        rf1.file = f1

        rf2 = RuleFile()
        rf2.type = output_entry
        rf2.file = f2

        rt1 = RuleTable()
        rt1.type = input_entry
        rt1.table = t1

        rt2 = RuleTable()
        rt2.type = output_entry
        rt2.table = t2

        self.__foowrapper_right_content = FooWrapper3(rule_name="rule1")
        self.__foowrapper_right_content.files.extend([rf1, rf2])
        self.__foowrapper_right_content.tables.extend([rt1, rt2])
        self.__foowrapper_right_content.options.append(opt1)

        rf1 = RuleFile()
        rf1.type = input_entry
        rf1.file = f1

        rf2 = RuleFile()
        rf2.type = output_entry
        rf2.file = f2

        rt1 = RuleTable()
        rt1.type = input_entry
        rt1.table = t1

        rt2 = RuleTable()
        rt2.type = output_entry
        rt2.table = t2

        self.__foowrapper_wrong_content1 = FooWrapper3(rule_name="rule2")
        self.__foowrapper_wrong_content1.files.extend([rf1, rf2])
        self.__foowrapper_wrong_content1.tables.extend([rt1, rt2])
        self.__foowrapper_wrong_content1.options.append(opt3)

        rf1 = RuleFile()
        rf1.type = input_entry
        rf1.file = f1

        rf2 = RuleFile()
        rf2.type = input_entry
        rf2.file = f3

        rf3 = RuleFile()
        rf3.type = output_entry
        rf3.file = f2

        rt1 = RuleTable()
        rt1.type = input_entry
        rt1.table = t1

        rt2 = RuleTable()
        rt2.type = output_entry
        rt2.table = t2

        self.__foowrapper_wrong_content2 = FooWrapper3(rule_name="rule3")
        self.__foowrapper_wrong_content2.files.extend([rf1, rf2, rf3])
        self.__foowrapper_wrong_content2.tables.extend([rt1, rt2])
        self.__foowrapper_wrong_content2.options.append(opt1)

        rf1 = RuleFile()
        rf1.type = input_entry
        rf1.file = f1

        rf2 = RuleFile()
        rf2.type = output_entry
        rf2.file = f2

        rt1 = RuleTable()
        rt1.type = input_entry
        rt1.table = t1

        rt2 = RuleTable()
        rt2.type = output_entry
        rt2.table = t2

        self.__foowrapper_wrong_content3 = FooWrapper3(rule_name="rule3")
        self.__foowrapper_wrong_content3.files.extend([rf1, rf2])
        self.__foowrapper_wrong_content3.tables.extend([rt1, rt2])
        self.__foowrapper_wrong_content3.options.append(opt2)

        rf1 = RuleFile()
        rf1.type = input_entry
        rf1.file = f1

        rf2 = RuleFile()
        rf2.type = output_entry
        rf2.file = f2

        rt1 = RuleTable()
        rt1.type = input_entry
        rt1.table = t1

        rt2 = RuleTable()
        rt2.type = output_entry
        rt2.table = t2

        self.__foowrapper_wrong_content4 = FooWrapper3(rule_name="rule3")
        self.__foowrapper_wrong_content4.files.extend([rf1, rf2])
        self.__foowrapper_wrong_content4.tables.extend([rt1, rt2])
        self.__foowrapper_wrong_content4.options.append(opt3)

        rf1 = RuleFile()
        rf1.type = input_entry
        rf1.file = f1

        rf2 = RuleFile()
        rf2.type = output_entry
        rf2.file = f2

        rt1 = RuleTable()
        rt1.type = input_entry
        rt1.table = t1

        rt2 = RuleTable()
        rt2.type = output_entry
        rt2.table = t2

        self.__foowrapper_wrong_content5 = FooWrapper3(rule_name="rule3")
        self.__foowrapper_wrong_content5.files.extend([rf1, rf2])
        self.__foowrapper_wrong_content5.tables.extend([rt1, rt2])

        ### TooLWrappers for follows

        rf1 = RuleFile()
        rf1.type = input_entry
        rf1.file = f1

        rf2 = RuleFile()
        rf2.type = output_entry
        rf2.file = f2

        self.__toolwrapper_first = FooWrapper2(rule_name="rule1")
        self.__toolwrapper_first.files.extend([rf1, rf2])

        f4 = IOFilePut(name="input1", path="file2.txt")
        f5 = IOFilePut(name="output1", path="file3.txt")

        rf1 = RuleFile()
        rf1.type = input_entry
        rf1.file = f4

        rf2 = RuleFile()
        rf2.type = output_entry
        rf2.file = f5

        rt1 = RuleTable()
        rt1.type = input_entry
        rt1.table = t1

        rt2 = RuleTable()
        rt2.type = output_entry
        rt2.table = t2

        self.__toolwrapper_second = FooWrapper3(rule_name="rule2")
        self.__toolwrapper_second.files.extend([rf1, rf2])
        self.__toolwrapper_second.tables.extend([rt1, rt2])
        self.__toolwrapper_second.options.append(opt1)


        ### ToolWrappers for are_input_ready

        s_root_path = PathFinder.find_src(os.path.dirname(os.path.realpath(__file__)))

        s_path_to_example_file_that_exists = s_root_path + "resources/input_File1.txt"

        f6 = IOFilePut(name="input1", path=s_path_to_example_file_that_exists)
        rf1 = RuleFile()
        rf1.type = input_entry
        rf1.file = f6

        rf2 = RuleFile()
        rf2.type = output_entry
        rf2.file = f2

        self.__toolwrapper_ready = FooWrapper2(rule_name="rule2")
        self.__toolwrapper_ready.files.extend([rf1, rf2])

        f7 = IOFilePut(name="input1", path="/not/existent/file")
        rf1 = RuleFile()
        rf1.type = input_entry
        rf1.file = f7

        rf2 = RuleFile()
        rf2.type = output_entry
        rf2.file = f2

        self.__toolwrapper_not_ready = FooWrapper2(rule_name="rule2")
        self.__toolwrapper_not_ready.files.extend([rf1, rf2])

    def test_eq(self):
        self.assertEqual(self.__toolwrapper1, self.__toolwrapper2)
        self.assertNotEqual(self.__toolwrapper1, self.__toolwrapper3)

    def test_is_content_respected(self):
        try:
            self.__foowrapper_right_content.is_content_respected()
        except WopMarsException:
            raise AssertionError('Should not raise exception')

        self.assertRaises(WopMarsException, self.__foowrapper_wrong_content1.is_content_respected)
        self.assertRaises(WopMarsException, self.__foowrapper_wrong_content2.is_content_respected)
        self.assertRaises(WopMarsException, self.__foowrapper_wrong_content3.is_content_respected)
        self.assertRaises(WopMarsException, self.__foowrapper_wrong_content4.is_content_respected)
        self.assertRaises(WopMarsException, self.__foowrapper_wrong_content5.is_content_respected)

    def test_follows(self):
        self.assertTrue(self.__toolwrapper_second.follows(self.__toolwrapper_first))
        self.assertFalse(self.__toolwrapper_first.follows(self.__toolwrapper_second))

    def test_are_inputs_ready(self):
        self.assertTrue(self.__toolwrapper_ready.are_inputs_ready())
        self.assertFalse(self.__toolwrapper_not_ready.are_inputs_ready())

if __name__ == '__main__':
    unittest.main()
