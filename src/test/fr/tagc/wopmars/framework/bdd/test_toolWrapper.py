import copy
import datetime
import os
import subprocess
import unittest
from unittest import TestCase

import time

from FooBase import FooBase
from FooWrapper1 import FooWrapper1
from FooWrapper2 import FooWrapper2
from src.main.fr.tagc.wopmars.framework.bdd.SQLManager import SQLManager
from src.main.fr.tagc.wopmars.framework.bdd.tables.IODbPut import IODbPut
from src.main.fr.tagc.wopmars.framework.bdd.tables.IOFilePut import IOFilePut
from src.main.fr.tagc.wopmars.framework.bdd.tables.ModificationTable import ModificationTable
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

        self.input_entry = Type(name="input")
        self.output_entry = Type(name="output")

        ### Toolwrappers for __eq__ test
        opt1 = Option(name="param1", value="1")

        f1 = IOFilePut(name="input1", path="file1.txt")
        f1.type = self.input_entry

        f2 = IOFilePut(name="output1", path="file2.txt")
        f2.type = self.output_entry

        self.__toolwrapper1 = ToolWrapper(rule_name="rule1")
        self.__toolwrapper1.files.extend([f1, f2])
        self.__toolwrapper1.options.append(opt1)

        opt1 = Option(name="param1", value="1")

        f1 = IOFilePut(name="input1", path="file1.txt")
        f1.type = self.input_entry

        f2 = IOFilePut(name="output1", path="file2.txt")
        f2.type = self.output_entry

        self.__toolwrapper2 = ToolWrapper(rule_name="rule2")
        self.__toolwrapper2.files.extend([f1, f2])
        self.__toolwrapper2.options.append(opt1)

        opt1 = Option(name="param2", value="2")

        f1 = IOFilePut(name="input1", path="file1.txt")
        f1.type = self.input_entry

        f2 = IOFilePut(name="output1", path="file2.txt")
        f2.type = self.output_entry

        self.__toolwrapper3 = ToolWrapper(rule_name="rule3")
        self.__toolwrapper3.files.extend([f1, f2])
        self.__toolwrapper3.options.append(opt1)

        ### ToolWrappers for content_respected
        opt1 = Option(name="param1", value="2")

        f1 = IOFilePut(name="input1", path="file1.txt")
        f1.type = self.input_entry

        f2 = IOFilePut(name="output1", path="file2.txt")
        f2.type = self.output_entry

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
        f1.type = self.input_entry

        f2 = IOFilePut(name="output1", path="file2.txt")
        f2.type = self.output_entry

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
        f1.type = self.input_entry

        f2 = IOFilePut(name="output1", path="file2.txt")
        f2.type = self.output_entry

        f3 = IOFilePut(name="input2", path="file2.txt")
        f3.type = self.input_entry

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
        f1.type = self.input_entry

        f2 = IOFilePut(name="output1", path="file2.txt")
        f2.type = self.output_entry

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
        f1.type = self.input_entry

        f2 = IOFilePut(name="output1", path="file2.txt")
        f2.type = self.output_entry

        t1 = IODbPut(name="FooBase")
        t1.table = t1

        t2 = IODbPut(name="FooBase")
        t2.table = t2

        self.__foowrapper_wrong_content4 = FooWrapper3(rule_name="rule3")
        self.__foowrapper_wrong_content4.files.extend([f1, f2])
        self.__foowrapper_wrong_content4.tables.extend([t1, t2])
        self.__foowrapper_wrong_content4.options.append(opt1)

        f1 = IOFilePut(name="input1", path="file1.txt")
        f1.type = self.input_entry

        f2 = IOFilePut(name="output1", path="file2.txt")
        f2.type = self.output_entry

        t1 = IODbPut(name="FooBase")
        t1.table = t1

        t2 = IODbPut(name="FooBase")
        t2.table = t2

        self.__foowrapper_wrong_content5 = FooWrapper3(rule_name="rule3")
        self.__foowrapper_wrong_content5.files.extend([f1, f2])
        self.__foowrapper_wrong_content5.tables.extend([t1, t2])

        ### TooLWrappers for follows

        f1 = IOFilePut(name="input1", path="file1.txt")
        f1.type = self.input_entry

        f2 = IOFilePut(name="output1", path="file2.txt")
        f2.type = self.output_entry

        self.__toolwrapper_first = FooWrapper2(rule_name="rule1")
        self.__toolwrapper_first.files.extend([f1, f2])

        f1 = IOFilePut(name="input1", path="file2.txt")
        f1.type = self.input_entry

        f2 = IOFilePut(name="output1", path="file3.txt")
        f2.type = self.output_entry

        self.__toolwrapper_second = FooWrapper2(rule_name="rule2")
        self.__toolwrapper_second.files.extend([f1, f2])

        ### ToolWrappers for are_input_ready

        s_root_path = PathFinder.find_src(os.path.dirname(os.path.realpath(__file__)))

        s_path_to_example_file_that_exists = s_root_path + "resources/input_File1.txt"

        f1 = IOFilePut(name="input1", path=s_path_to_example_file_that_exists)
        f1.type = self.input_entry

        f2 = IOFilePut(name="output1", path="file2.txt")
        f2.type = self.output_entry

        self.__toolwrapper_ready = FooWrapper2(rule_name="rule2")
        self.__toolwrapper_ready.files.extend([f1, f2])

        f1 = IOFilePut(name="input1", path="/not/existent/file")
        f1.type = self.input_entry

        f2 = IOFilePut(name="output1", path="file2.txt")
        f2.type = self.output_entry

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

        SQLManager.instance().get_session().add_all([FooBase(name="test " + str(i)) for i in range(5)])
        SQLManager.instance().get_session().commit()

        t1 = IODbPut(name="FooBase")
        t1.type = self.input_entry

        toolwrapper_ready2 = FooWrapper2(rule_name="rule2")
        toolwrapper_ready2.tables.append(t1)
        self.assertTrue(toolwrapper_ready2.are_inputs_ready())

        SQLManager.instance().drop(FooBase.__tablename__)

        self.assertFalse(toolwrapper_ready2.are_inputs_ready())

    def test_same_input_than(self):

        moment = datetime.datetime.fromtimestamp(time.time())

        t1 = IODbPut(name="FooBase")
        t1.type = self.input_entry
        modif = ModificationTable(table_name="FooBase", date=moment)
        modif.tables.append(t1)

        t2 = IODbPut(name="FooBase")
        t2.type = self.input_entry
        modif = ModificationTable(table_name="FooBase", date=moment)
        modif.tables.append(t2)

        f1 = IOFilePut(name="input1", path="path1", used_at=moment, size=0)
        f1.type = self.input_entry

        f2 = IOFilePut(name="input1", path="path1", used_at=moment, size=0)
        f2.type = self.input_entry

        toolwrapper1 = FooWrapper2(rule_name="rule1")
        toolwrapper1.files.append(f1)
        toolwrapper1.tables.append(t1)

        toolwrapper2 = FooWrapper2(rule_name="rule1")
        toolwrapper2.files.append(f2)
        toolwrapper2.tables.append(t2)

        t3 = IODbPut(name="FooBase")
        t3.type = self.input_entry
        modif = ModificationTable(table_name="FooBase", date=moment)
        modif.tables.append(t3)

        f3 = IOFilePut(name="input1", path="path1", used_at=datetime.datetime.fromtimestamp(time.time()), size=0)
        f3.type = self.input_entry

        toolwrapper3 = FooWrapper2(rule_name="rule1")
        toolwrapper3.files.append(f3)
        toolwrapper3.tables.append(t3)

        self.assertTrue(toolwrapper1.same_input_than(toolwrapper2))
        self.assertFalse(toolwrapper1.same_input_than(toolwrapper3))

    def test_is_output_ok(self):

        moment = datetime.datetime.fromtimestamp(time.time())
        t1 = IODbPut(name="FooBase")
        t1.type = self.input_entry
        t1.used_at = moment
        modif = ModificationTable(table_name="FooBase", date=moment)
        modif.tables.append(t1)

        root = PathFinder.find_src(os.path.dirname(os.path.realpath(__file__)))
        path_f1 = root + "resources/outputs/path1"
        time.sleep(2)
        p = subprocess.Popen(["touch", path_f1])
        p.wait()

        f1 = IOFilePut(name="input1", path=path_f1, used_at=datetime.datetime.fromtimestamp(os.path.getmtime(path_f1)),
                       size=os.path.getsize(path_f1))
        f1.type = self.output_entry

        toolwrapper1 = FooWrapper2(rule_name="rule1")
        toolwrapper1.files.append(f1)
        toolwrapper1.tables.append(t1)


        f1 = IOFilePut(name="input1", path=path_f1, used_at=datetime.datetime.fromtimestamp(os.path.getmtime(path_f1)),
                       size=os.path.getsize(path_f1))

        f1.type = self.output_entry

        moment = datetime.datetime.fromtimestamp(time.time())
        t1 = IODbPut(name="FooBase")
        t1.type = self.input_entry
        t1.used_at = moment
        modif = ModificationTable(table_name="FooBase", date=moment)
        modif.tables.append(t1)

        toolwrapper2 = FooWrapper2(rule_name="rule1")
        toolwrapper2.files.append(f1)
        toolwrapper2.tables.append(t1)

        self.assertTrue(toolwrapper1.is_output_ok())
        self.assertFalse(toolwrapper2.is_output_ok())

    def tearDown(self):
        SQLManager.drop_all()
        PathFinder.dir_content_remove("/home/giffon/Documents/wopmars/src/resources/outputs/")
        OptionManager._drop()
        SQLManager._drop()

if __name__ == '__main__':
    unittest.main()
