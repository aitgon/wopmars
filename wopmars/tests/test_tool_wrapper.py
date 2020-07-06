import os
import shutil
import subprocess
import time
import unittest
from unittest import TestCase

from wopmars.tests.resource.model.FooBase import FooBase
from wopmars.tests.resource.wrapper.FooWrapper2 import FooWrapper2
from wopmars.tests.resource.wrapper.FooWrapper3 import FooWrapper3
from wopmars.SQLManager import SQLManager
from wopmars.models.TableInputOutputInformation import TableInputOutputInformation
from wopmars.models.FileInputOutputInformation import FileInputOutputInformation
from wopmars.models.TableModificationTime import TableModificationTime
from wopmars.models.Option import Option
from wopmars.models.ToolWrapper import ToolWrapper
from wopmars.models.TypeInputOrOutput import TypeInputOrOutput
from wopmars.utils.OptionManager import OptionManager
from wopmars.utils.PathManager import PathManager
from wopmars.utils.WopMarsException import WopMarsException
from wopmars.utils.various import get_current_time
from wopmars.utils.various import get_mtime


class TestToolWrapper(TestCase):

    def setUp(self):

        self.test_path = PathManager.get_test_path()
        OptionManager.initial_test_setup()  # Set tests arguments
        SQLManager.instance().create_all()  # Create database with tables

        set_tw_to_add = set()
        self.__session = SQLManager.instance().get_session()

        self.input_entry = TypeInputOrOutput(is_input=True)
        self.output_entry = TypeInputOrOutput(is_input=False)

        # Toolwrappers for __eq__ test_bak
        opt1 = Option(name="param1", value="1")

        f1 = FileInputOutputInformation(file_key="input1", path="file1.txt")
        f1.relation_file_or_tableioinfo_to_typeio = self.input_entry

        f2 = FileInputOutputInformation(file_key="output1", path="file2.txt")
        f2.relation_file_or_tableioinfo_to_typeio = self.output_entry

        self.__toolwrapper1 = ToolWrapper(rule_name="rule1")
        self.__toolwrapper1.relation_toolwrapper_to_fileioinfo.extend([f1, f2])
        self.__toolwrapper1.relation_toolwrapper_to_option.append(opt1)

        opt1 = Option(name="param1", value="1")

        f1 = FileInputOutputInformation(file_key="input1", path="file1.txt")
        f1.relation_file_or_tableioinfo_to_typeio = self.input_entry

        f2 = FileInputOutputInformation(file_key="output1", path="file2.txt")
        f2.relation_file_or_tableioinfo_to_typeio = self.output_entry

        self.__toolwrapper2 = ToolWrapper(rule_name="rule2")
        self.__toolwrapper2.relation_toolwrapper_to_fileioinfo.extend([f1, f2])
        self.__toolwrapper2.relation_toolwrapper_to_option.append(opt1)

        opt1 = Option(name="param2", value="2")

        f1 = FileInputOutputInformation(file_key="input1", path="file1.txt")
        f1.relation_file_or_tableioinfo_to_typeio = self.input_entry

        f2 = FileInputOutputInformation(file_key="output1", path="file2.txt")
        f2.relation_file_or_tableioinfo_to_typeio = self.output_entry

        self.__toolwrapper3 = ToolWrapper(rule_name="rule3")
        self.__toolwrapper3.relation_toolwrapper_to_fileioinfo.extend([f1, f2])
        self.__toolwrapper3.relation_toolwrapper_to_option.append(opt1)

        # ToolWrappers for content_respected
        opt1 = Option(name="param1", value="2")

        f1 = FileInputOutputInformation(file_key="input1", path="file1.txt")
        f1.relation_file_or_tableioinfo_to_typeio = self.input_entry

        f2 = FileInputOutputInformation(file_key="output1", path="file2.txt")
        f2.relation_file_or_tableioinfo_to_typeio = self.output_entry

        t1 = TableInputOutputInformation(model_py_path="FooBase", table_key="FooBase", table_name="FooBase")
        t1.set_table(FooBase)
        t1.model_declarative_meta = FooBase
        t1.table = t1
        t1.relation_file_or_tableioinfo_to_typeio = self.input_entry

        t2 = TableInputOutputInformation(model_py_path="FooBase", table_key="FooBase", table_name="FooBase")
        t2.set_table(FooBase)
        t2.model_declarative_meta = FooBase
        t2.table = t2
        t2.relation_file_or_tableioinfo_to_typeio = self.output_entry

        self.__foowrapper_right_content = FooWrapper3(rule_name="rule1")
        self.__foowrapper_right_content.relation_toolwrapper_to_fileioinfo.extend([f1, f2])
        self.__foowrapper_right_content.relation_toolwrapper_to_tableioinfo.extend([t1, t2])
        self.__foowrapper_right_content.relation_toolwrapper_to_option.append(opt1)

        opt1 = Option(name="param1", value="String")

        f1 = FileInputOutputInformation(file_key="input1", path="file1.txt")
        f1.relation_file_or_tableioinfo_to_typeio = self.input_entry

        f2 = FileInputOutputInformation(file_key="output1", path="file2.txt")
        f2.relation_file_or_tableioinfo_to_typeio = self.output_entry

        t1 = TableInputOutputInformation(model_py_path="FooBase", table_key="FooBase", table_name="FooBase")
        # t1.set_table(FooBase)
        t1.model_declarative_meta = FooBase
        t1.table = t1

        t2 = TableInputOutputInformation(model_py_path="FooBase", table_key="FooBase", table_name="FooBase")
        # t2.set_table(FooBase)
        t2.model_declarative_meta = FooBase
        t2.table = t2

        self.__foowrapper_wrong_content1 = FooWrapper3(rule_name="rule2")
        self.__foowrapper_wrong_content1.relation_toolwrapper_to_fileioinfo.extend([f1, f2])
        self.__foowrapper_wrong_content1.relation_toolwrapper_to_tableioinfo.extend([t1, t2])
        self.__foowrapper_wrong_content1.relation_toolwrapper_to_option.append(opt1)

        opt1 = Option(name="param2", value="2")

        f1 = FileInputOutputInformation(file_key="input1", path="file1.txt")
        f1.relation_file_or_tableioinfo_to_typeio = self.input_entry

        f2 = FileInputOutputInformation(file_key="output1", path="file2.txt")
        f2.relation_file_or_tableioinfo_to_typeio = self.output_entry

        f3 = FileInputOutputInformation(file_key="input2", path="file2.txt")
        f3.relation_file_or_tableioinfo_to_typeio = self.input_entry

        t1 = TableInputOutputInformation(model_py_path="FooBase", table_key="FooBase", table_name="FooBase")
        # t1.set_table(FooBase)
        t1.model_declarative_meta = FooBase
        t1.table = t1

        t2 = TableInputOutputInformation(model_py_path="FooBase", table_key="FooBase", table_name="FooBase")
        # t2.set_table(FooBase)
        t2.model_declarative_meta = FooBase
        t2.table = t2

        self.__foowrapper_wrong_content2 = FooWrapper3(rule_name="rule3")
        self.__foowrapper_wrong_content2.relation_toolwrapper_to_fileioinfo.extend([f1, f2, f3])
        self.__foowrapper_wrong_content2.relation_toolwrapper_to_tableioinfo.extend([t1, t2])
        self.__foowrapper_wrong_content2.relation_toolwrapper_to_option.append(opt1)

        opt1 = Option(name="param2", value="2")

        f1 = FileInputOutputInformation(file_key="input1", path="file1.txt")
        f1.relation_file_or_tableioinfo_to_typeio = self.input_entry

        f2 = FileInputOutputInformation(file_key="output1", path="file2.txt")
        f2.relation_file_or_tableioinfo_to_typeio = self.output_entry

        t1 = TableInputOutputInformation(model_py_path="FooBase", table_key="FooBase", table_name="FooBase")
        # t1.set_table(FooBase)
        t1.model_declarative_meta = FooBase
        t1.table = t1

        t2 = TableInputOutputInformation(model_py_path="FooBase", table_key="FooBase", table_name="FooBase")
        # t2.set_table(FooBase)
        t2.model_declarative_meta = FooBase
        t2.table = t2

        self.__foowrapper_wrong_content3 = FooWrapper3(rule_name="rule3")
        self.__foowrapper_wrong_content3.relation_toolwrapper_to_fileioinfo.extend([f1, f2])
        self.__foowrapper_wrong_content3.relation_toolwrapper_to_tableioinfo.extend([t1, t2])
        self.__foowrapper_wrong_content3.relation_toolwrapper_to_option.append(opt1)

        opt1 = Option(name="param1", value="String")

        f1 = FileInputOutputInformation(file_key="input1", path="file1.txt")
        f1.relation_file_or_tableioinfo_to_typeio = self.input_entry

        f2 = FileInputOutputInformation(file_key="output1", path="file2.txt")
        f2.relation_file_or_tableioinfo_to_typeio = self.output_entry

        t1 = TableInputOutputInformation(model_py_path="FooBase", table_key="FooBase", table_name="FooBase")
        # t1.set_table(FooBase)
        t1.model_declarative_meta = FooBase
        t1.table = t1

        t2 = TableInputOutputInformation(model_py_path="FooBase", table_key="FooBase", table_name="FooBase")
        # t2.set_table(FooBase)
        t2.model_declarative_meta = FooBase
        t2.table = t2

        self.__foowrapper_wrong_content4 = FooWrapper3(rule_name="rule3")
        self.__foowrapper_wrong_content4.relation_toolwrapper_to_fileioinfo.extend([f1, f2])
        self.__foowrapper_wrong_content4.relation_toolwrapper_to_tableioinfo.extend([t1, t2])
        self.__foowrapper_wrong_content4.relation_toolwrapper_to_option.append(opt1)

        f1 = FileInputOutputInformation(file_key="input1", path="file1.txt")
        f1.relation_file_or_tableioinfo_to_typeio = self.input_entry

        f2 = FileInputOutputInformation(file_key="output1", path="file2.txt")
        f2.relation_file_or_tableioinfo_to_typeio = self.output_entry

        t1 = TableInputOutputInformation(model_py_path="FooBase", table_key="FooBase", table_name="FooBase")
        # t1.set_table(FooBase)
        t1.model_declarative_meta = FooBase
        t1.table = t1

        t2 = TableInputOutputInformation(model_py_path="FooBase", table_key="FooBase", table_name="FooBase")
        # t2.set_table(FooBase)
        t2.model_declarative_meta = FooBase
        t2.table = t2

        self.__foowrapper_wrong_content5 = FooWrapper3(rule_name="rule3")
        self.__foowrapper_wrong_content5.relation_toolwrapper_to_fileioinfo.extend([f1, f2])
        self.__foowrapper_wrong_content5.relation_toolwrapper_to_tableioinfo.extend([t1, t2])

        # TooLWrappers for follows

        f1 = FileInputOutputInformation(file_key="input1", path="file1.txt")
        f1.relation_file_or_tableioinfo_to_typeio = self.input_entry

        f2 = FileInputOutputInformation(file_key="output1", path="file2.txt")
        f2.relation_file_or_tableioinfo_to_typeio = self.output_entry

        self.__toolwrapper_first = FooWrapper2(rule_name="rule1")
        self.__toolwrapper_first.relation_toolwrapper_to_fileioinfo.extend([f1, f2])

        f1 = FileInputOutputInformation(file_key="input1", path="file2.txt")
        f1.relation_file_or_tableioinfo_to_typeio = self.input_entry

        f2 = FileInputOutputInformation(file_key="output1", path="file3.txt")
        f2.relation_file_or_tableioinfo_to_typeio = self.output_entry

        self.__toolwrapper_second = FooWrapper2(rule_name="rule2")
        self.__toolwrapper_second.relation_toolwrapper_to_fileioinfo.extend([f1, f2])

        # ToolWrappers for are_input_ready

        s_path_to_example_file_that_exists = os.path.join(self.test_path, "resource/input_files/input_file1.txt")

        f1 = FileInputOutputInformation(file_key="input1", path=s_path_to_example_file_that_exists)
        f1.relation_file_or_tableioinfo_to_typeio = self.input_entry

        f2 = FileInputOutputInformation(file_key="output1", path="file2.txt")
        f2.relation_file_or_tableioinfo_to_typeio = self.output_entry

        self.__toolwrapper_ready = FooWrapper2(rule_name="rule2")
        self.__toolwrapper_ready.relation_toolwrapper_to_fileioinfo.extend([f1, f2])

        f1 = FileInputOutputInformation(file_key="input1", path="/not/existent/file")
        f1.relation_file_or_tableioinfo_to_typeio = self.input_entry

        f2 = FileInputOutputInformation(file_key="output1", path="file2.txt")
        f2.relation_file_or_tableioinfo_to_typeio = self.output_entry

        self.__toolwrapper_not_ready = FooWrapper2(rule_name="rule2")
        self.__toolwrapper_not_ready.relation_toolwrapper_to_fileioinfo.extend([f1, f2])

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

        SQLManager.instance().get_session().add_all([FooBase(name="test_bak " + str(i)) for i in range(5)])
        SQLManager.instance().get_session().commit()

        t1 = TableInputOutputInformation(model_py_path="FooBase", table_key="FooBase", table_name="FooBase")
        t1.set_table(FooBase)
        t1.model_declarative_meta = FooBase
        t1.relation_file_or_tableioinfo_to_typeio = self.input_entry

        toolwrapper_ready2 = FooWrapper2(rule_name="rule2")
        toolwrapper_ready2.relation_toolwrapper_to_tableioinfo.append(t1)
        self.assertTrue(toolwrapper_ready2.are_inputs_ready())
        # this tests does not work with mysql and postgresql
        if not SQLManager.instance().engine.url.drivername in ['mysql', 'postgresql']:
            SQLManager.instance().drop(FooBase.__tablename__)
            self.assertFalse(toolwrapper_ready2.are_inputs_ready())

    def test_same_input_than(self):

        mtime_epoch_millis1, mtime_human1 = get_current_time()
        # moment = mtime_epoch_millis

        t1 = TableInputOutputInformation(model_py_path="FooBase", table_key="FooBase", table_name="FooBase")
        # t1.set_table(FooBase)
        t1.model_declarative_meta = FooBase
        t1.relation_file_or_tableioinfo_to_typeio = self.input_entry
        modif = TableModificationTime(table_name="FooBase", mtime_epoch_millis=mtime_epoch_millis1, mtime_human=mtime_human1)
        modif.relation_tablemodiftime_to_tableioinfo.append(t1)

        t2 = TableInputOutputInformation(model_py_path="FooBase", table_key="FooBase", table_name="FooBase")
        # t2.set_table(FooBase)
        t2.model_declarative_meta = FooBase
        t2.relation_file_or_tableioinfo_to_typeio = self.input_entry
        modif = TableModificationTime(table_name="FooBase", mtime_epoch_millis=mtime_epoch_millis1, mtime_human=mtime_human1)
        modif.relation_tablemodiftime_to_tableioinfo.append(t2)

        f1 = FileInputOutputInformation(file_key="input1", path="path1", mtime_epoch_millis=mtime_epoch_millis1, size=0)
        f1.relation_file_or_tableioinfo_to_typeio = self.input_entry

        f2 = FileInputOutputInformation(file_key="input1", path="path1", mtime_epoch_millis=mtime_epoch_millis1, size=0)
        f2.relation_file_or_tableioinfo_to_typeio = self.input_entry

        toolwrapper1 = FooWrapper2(rule_name="rule1")
        toolwrapper1.relation_toolwrapper_to_fileioinfo.append(f1)
        toolwrapper1.relation_toolwrapper_to_tableioinfo.append(t1)

        toolwrapper2 = FooWrapper2(rule_name="rule1")
        toolwrapper2.relation_toolwrapper_to_fileioinfo.append(f2)
        toolwrapper2.relation_toolwrapper_to_tableioinfo.append(t2)

        t3 = TableInputOutputInformation(model_py_path="FooBase", table_key="FooBase", table_name="FooBase")
        # t3.set_table(FooBase)
        t3.model_declarative_meta = FooBase
        t3.relation_file_or_tableioinfo_to_typeio = self.input_entry
        modif = TableModificationTime(table_name="FooBase", mtime_epoch_millis=mtime_epoch_millis1, mtime_human=mtime_human1)
        modif.relation_tablemodiftime_to_tableioinfo.append(t3)

        time.sleep(0.05)
        mtime_epoch_millis2, mtime_human2 = get_current_time()
        f3 = FileInputOutputInformation(file_key="input1", path="path1", mtime_epoch_millis=mtime_epoch_millis2, size=0)
        f3.relation_file_or_tableioinfo_to_typeio = self.input_entry

        toolwrapper3 = FooWrapper2(rule_name="rule1")
        toolwrapper3.relation_toolwrapper_to_fileioinfo.append(f3)
        toolwrapper3.relation_toolwrapper_to_tableioinfo.append(t3)

        self.assertTrue(toolwrapper1.same_input_than(toolwrapper2))
        self.assertFalse(toolwrapper1.same_input_than(toolwrapper3))

    def test_is_output_ok(self):

        mtime_epoch_millis, mtime_human = get_current_time()
        moment = mtime_epoch_millis
        t1 = TableInputOutputInformation(model_py_path="FooBase", table_key="FooBase", table_name="FooBase")
        # t1.set_table(FooBase)
        t1.model_declarative_meta = FooBase
        t1.relation_file_or_tableioinfo_to_typeio = self.input_entry
        t1.mtime_epoch_millis = moment
        modif = TableModificationTime(table_name="FooBase", mtime_epoch_millis=moment, mtime_human=mtime_human)
        modif.relation_tablemodiftime_to_tableioinfo.append(t1)

        path_f1 = os.path.join(self.test_path, "outdir/path1")
        time.sleep(2)
        p = subprocess.Popen(["touch", path_f1])
        p.wait()

        f1 = FileInputOutputInformation(file_key="input1", path=path_f1, mtime_epoch_millis=get_mtime(path_f1),
                                        size=os.path.getsize(path_f1))
        f1.relation_file_or_tableioinfo_to_typeio = self.output_entry

        toolwrapper1 = FooWrapper2(rule_name="rule1")
        toolwrapper1.relation_toolwrapper_to_fileioinfo.append(f1)
        toolwrapper1.relation_toolwrapper_to_tableioinfo.append(t1)

        f1 = FileInputOutputInformation(file_key="input1", path=path_f1, mtime_epoch_millis=get_mtime(path_f1),
                                        size=os.path.getsize(path_f1))

        f1.relation_file_or_tableioinfo_to_typeio = self.output_entry
        mtime_epoch_millis, mtime_human = get_current_time()
        moment = mtime_epoch_millis
        t1 = TableInputOutputInformation(model_py_path="FooBase", table_key="FooBase", table_name="FooBase")
        # t1.set_table(FooBase)
        t1.model_declarative_meta = FooBase
        t1.relation_file_or_tableioinfo_to_typeio = self.input_entry
        t1.mtime_epoch_millis = moment
        modif = TableModificationTime(table_name="FooBase", mtime_epoch_millis=moment, mtime_human=mtime_human)
        modif.relation_tablemodiftime_to_tableioinfo.append(t1)

        toolwrapper2 = FooWrapper2(rule_name="rule1")
        toolwrapper2.relation_toolwrapper_to_fileioinfo.append(f1)
        toolwrapper2.relation_toolwrapper_to_tableioinfo.append(t1)

    def tearDown(self):
        SQLManager.instance().get_session().close()
        SQLManager.instance().drop_all()
        shutil.rmtree(os.path.join(self.test_path, "outdir"), ignore_errors=True)
        OptionManager._drop()
        SQLManager._drop()

if __name__ == '__main__':
    unittest.main()
