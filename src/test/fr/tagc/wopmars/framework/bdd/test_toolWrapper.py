import os
import unittest
from unittest import TestCase

from FooWrapper1 import FooWrapper1
from FooWrapper2 import FooWrapper2
from src.main.fr.tagc.wopmars.framework.bdd.SQLManager import SQLManager
from src.main.fr.tagc.wopmars.framework.bdd.tables.IODbPut import IODbPut
from src.main.fr.tagc.wopmars.framework.bdd.tables.IOFilePut import IOFilePut
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

        ### Toolwrappers for __eq__ test
        opt1 = Option(name="param1", value="1")

        f1 = IOFilePut(name="input1", path="file1.txt")
        f1.type = input_entry

        f2 = IOFilePut(name="output1", path="file2.txt")
        f2.type = output_entry

        self.__toolwrapper1 = ToolWrapper(rule_name="rule1")
        self.__toolwrapper1.files.extend([f1, f2])
        self.__toolwrapper1.options.append(opt1)

        opt1 = Option(name="param1", value="1")

        f1 = IOFilePut(name="input1", path="file1.txt")
        f1.type = input_entry

        f2 = IOFilePut(name="output1", path="file2.txt")
        f2.type = output_entry

        self.__toolwrapper2 = ToolWrapper(rule_name="rule2")
        self.__toolwrapper2.files.extend([f1, f2])
        self.__toolwrapper2.options.append(opt1)

        opt1 = Option(name="param2", value="2")

        f1 = IOFilePut(name="input1", path="file1.txt")
        f1.type = input_entry

        f2 = IOFilePut(name="output1", path="file2.txt")
        f2.type = output_entry

        self.__toolwrapper3 = ToolWrapper(rule_name="rule3")
        self.__toolwrapper3.files.extend([f1, f2])
        self.__toolwrapper3.options.append(opt1)

        ### ToolWrappers for content_respected
        opt1 = Option(name="param1", value="2")

        f1 = IOFilePut(name="input1", path="file1.txt")
        f1.type = input_entry

        f2 = IOFilePut(name="output1", path="file2.txt")
        f2.type = output_entry

        t1 = IODbPut(name="FooBase")
        t1.table = t1

        t2 = IODbPut(name="FooBase")
        t2.table = t2

        self.__foowrapper_right_content = FooWrapper3(rule_name="rule1")
        self.__foowrapper_right_content.files.extend([f1, f2])
        self.__foowrapper_right_content.tables.extend([t1, t2])
        self.__foowrapper_right_content.options.append(opt1)

        opt1 = Option(name="param1", value="String")

        f1 = IOFilePut(name="input1", path="file1.txt")
        f1.type = input_entry

        f2 = IOFilePut(name="output1", path="file2.txt")
        f2.type = output_entry

        t1 = IODbPut(name="FooBase")
        t1.table = t1

        t2 = IODbPut(name="FooBase")
        t2.table = t2

        self.__foowrapper_wrong_content1 = FooWrapper3(rule_name="rule2")
        self.__foowrapper_wrong_content1.files.extend([f1, f2])
        self.__foowrapper_wrong_content1.tables.extend([t1, t2])
        self.__foowrapper_wrong_content1.options.append(opt1)

        opt1 = Option(name="param2", value="2")

        f1 = IOFilePut(name="input1", path="file1.txt")
        f1.type = input_entry

        f2 = IOFilePut(name="output1", path="file2.txt")
        f2.type = output_entry

        f3 = IOFilePut(name="input2", path="file2.txt")
        f3.type = input_entry

        t1 = IODbPut(name="FooBase")
        t1.table = t1

        t2 = IODbPut(name="FooBase")
        t2.table = t2

        self.__foowrapper_wrong_content2 = FooWrapper3(rule_name="rule3")
        self.__foowrapper_wrong_content2.files.extend([f1, f2, f3])
        self.__foowrapper_wrong_content2.tables.extend([t1, t2])
        self.__foowrapper_wrong_content2.options.append(opt1)

        opt1 = Option(name="param2", value="2")

        f1 = IOFilePut(name="input1", path="file1.txt")
        f1.type = input_entry

        f2 = IOFilePut(name="output1", path="file2.txt")
        f2.type = output_entry

        t1 = IODbPut(name="FooBase")
        t1.table = t1

        t2 = IODbPut(name="FooBase")
        t2.table = t2

        self.__foowrapper_wrong_content3 = FooWrapper3(rule_name="rule3")
        self.__foowrapper_wrong_content3.files.extend([f1, f2])
        self.__foowrapper_wrong_content3.tables.extend([t1, t2])
        self.__foowrapper_wrong_content3.options.append(opt1)

        opt1 = Option(name="param1", value="String")

        f1 = IOFilePut(name="input1", path="file1.txt")
        f1.type = input_entry

        f2 = IOFilePut(name="output1", path="file2.txt")
        f2.type = output_entry

        t1 = IODbPut(name="FooBase")
        t1.table = t1

        t2 = IODbPut(name="FooBase")
        t2.table = t2

        self.__foowrapper_wrong_content4 = FooWrapper3(rule_name="rule3")
        self.__foowrapper_wrong_content4.files.extend([f1, f2])
        self.__foowrapper_wrong_content4.tables.extend([t1, t2])
        self.__foowrapper_wrong_content4.options.append(opt1)

        f1 = IOFilePut(name="input1", path="file1.txt")
        f1.type = input_entry

        f2 = IOFilePut(name="output1", path="file2.txt")
        f2.type = output_entry

        t1 = IODbPut(name="FooBase")
        t1.table = t1

        t2 = IODbPut(name="FooBase")
        t2.table = t2

        self.__foowrapper_wrong_content5 = FooWrapper3(rule_name="rule3")
        self.__foowrapper_wrong_content5.files.extend([f1, f2])
        self.__foowrapper_wrong_content5.tables.extend([t1, t2])

        ### TooLWrappers for follows

        f1 = IOFilePut(name="input1", path="file1.txt")
        f1.type = input_entry

        f2 = IOFilePut(name="output1", path="file2.txt")
        f2.type = output_entry

        self.__toolwrapper_first = FooWrapper2(rule_name="rule1")
        self.__toolwrapper_first.files.extend([f1, f2])

        f1 = IOFilePut(name="input1", path="file2.txt")
        f1.type = input_entry

        f2 = IOFilePut(name="output1", path="file3.txt")
        f2.type = output_entry

        self.__toolwrapper_second = FooWrapper2(rule_name="rule2")
        self.__toolwrapper_second.files.extend([f1, f2])

        ### ToolWrappers for are_input_ready

        s_root_path = PathFinder.find_src(os.path.dirname(os.path.realpath(__file__)))

        s_path_to_example_file_that_exists = s_root_path + "resources/input_File1.txt"

        f1 = IOFilePut(name="input1", path=s_path_to_example_file_that_exists)
        f1.type = input_entry

        f2 = IOFilePut(name="output1", path="file2.txt")
        f2.type = output_entry

        self.__toolwrapper_ready = FooWrapper2(rule_name="rule2")
        self.__toolwrapper_ready.files.extend([f1, f2])

        f1 = IOFilePut(name="input1", path="/not/existent/file")
        f1.type = input_entry

        f2 = IOFilePut(name="output1", path="file2.txt")
        f2.type = output_entry

        self.__toolwrapper_not_ready = FooWrapper2(rule_name="rule2")
        self.__toolwrapper_not_ready.files.extend([f1, f2])

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

    def tearDown(self):
        SQLManager.drop_all()
        PathFinder.dir_content_remove("/home/giffon/Documents/wopmars/src/resources/outputs/")
        OptionManager._drop()
        SQLManager._drop()

if __name__ == '__main__':
    unittest.main()
