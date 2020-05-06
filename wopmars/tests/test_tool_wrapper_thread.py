import shutil
import time
import unittest
from unittest import TestCase

from wopmars.tests.resource.model.FooBase import FooBase
from wopmars.tests.resource.wrapper.FooWrapper5 import FooWrapper5
from wopmars.tests.resource.wrapper.sprintFive.Add import Add
from wopmars.tests.resource.wrapper.sprintFive.Query import Query
from wopmars.SQLManager import SQLManager
from wopmars.models.TableInputOutputInformation import TableInputOutputInformation
from wopmars.models.FileInputOutputInformation import FileInputOutputInformation
from wopmars.models.TableModificationTime import TableModificationTime
from wopmars.models.Option import Option
from wopmars.models.TypeInputOrOutput import TypeInputOrOutput
from wopmars.ToolWrapperThread import ToolWrapperThread
from wopmars.utils.OptionManager import OptionManager
from wopmars.utils.PathManager import PathManager
from wopmars.utils.various import get_current_time


class TestToolWrapperThread(TestCase):

    def setUp(self):
        OptionManager.initial_test_setup()  # Set tests arguments
        SQLManager.instance().create_all()  # Create database with tables

        [SQLManager.instance().get_session().add(FooBase(name="foo " + str(i))) for i in range(10000)]
        SQLManager.instance().get_session().commit()

    def test_run(self):

        input_entry = TypeInputOrOutput(is_input=True)
        output_entry = TypeInputOrOutput(is_input=False)

        f1 = FileInputOutputInformation(file_key="input1", path="resource/input_files/input_file1.txt")
        f1.relation_file_or_tableioinfo_to_typeio = input_entry

        f2 = FileInputOutputInformation(file_key="output1", path="outdir/output_file1.txt")
        f2.relation_file_or_tableioinfo_to_typeio = output_entry

        t1 = TableInputOutputInformation(model_py_path="FooBase", table_key="FooBase", table_name="FooBase")
        t1.set_table(FooBase)
        t1.relation_file_or_tableioinfo_to_typeio = output_entry
        timestamp_millis, timestamp_human = get_current_time()
        modification_table_entry = TableModificationTime(mtime_epoch_millis=timestamp_millis, table_name=t1.table_name)
        t1.modification = modification_table_entry

        tw1 = FooWrapper5(rule_name="rule1")
        tw1.relation_toolwrapper_to_fileioinfo.extend([f1, f2])
        tw1.relation_toolwrapper_to_tableioinfo.append(t1)

        f12 = FileInputOutputInformation(file_key="input1", path="resource/input_files/input_file1.txt")
        f12.relation_file_or_tableioinfo_to_typeio = input_entry

        f22 = FileInputOutputInformation(file_key="output1", path="outdir/output_file1.txt")
        f22.relation_file_or_tableioinfo_to_typeio = output_entry

        t12 = TableInputOutputInformation(model_py_path="FooBase", table_key="FooBase", table_name="FooBase")
        t12.set_table(FooBase)
        t12.relation_file_or_tableioinfo_to_typeio = output_entry
        timestamp_millis, timestamp_human = get_current_time()
        modification_table_entry = TableModificationTime(
            mtime_epoch_millis=timestamp_millis, table_name=t12.table_name)
        t12.modification = modification_table_entry

        tw2 = FooWrapper5(rule_name="rule2")
        tw2.relation_toolwrapper_to_fileioinfo.extend([f12, f22])
        tw2.relation_toolwrapper_to_tableioinfo.append(t12)

        f13 = FileInputOutputInformation(file_key="input1", path="resource/input_files/input_file1.txt")
        f13.relation_file_or_tableioinfo_to_typeio = input_entry

        f23 = FileInputOutputInformation(file_key="output1", path="outdir/output_file1.txt")
        f23.relation_file_or_tableioinfo_to_typeio = output_entry

        t13 = TableInputOutputInformation(model_py_path="FooBase", table_key="FooBase", table_name="FooBase")
        t13.set_table(FooBase)
        t13.relation_file_or_tableioinfo_to_typeio = output_entry
        timestamp_millis, timestamp_human = get_current_time()
        modification_table_entry = TableModificationTime(
            mtime_epoch_millis=timestamp_millis, table_name=t13.table_name)
        t13.modification = modification_table_entry

        tw3 = FooWrapper5(rule_name="rule3")
        tw3.relation_toolwrapper_to_fileioinfo.extend([f13, f23])
        tw3.relation_toolwrapper_to_tableioinfo.append(t13)

        tt1 = ToolWrapperThread(tw1)
        tt2 = ToolWrapperThread(tw2)
        tt3 = ToolWrapperThread(tw3)

        tt1.start()
        tt2.start()
        tt3.start()

        tt1.join()
        tt2.join()
        tt3.join()

        self.assertEqual(len(SQLManager.instance().get_session().query(FooBase).filter(FooBase.name.like('Foowrapper5 - %')).all()), 3000)

    def test_run_commit_vs_query(self):
        # this tests does not work with mysql and postgresql
        if not SQLManager.instance().engine.url.drivername in ['mysql', 'postgresql']:
            input_entry = TypeInputOrOutput(is_input=True)
            output_entry = TypeInputOrOutput(is_input=False)

            f1 = FileInputOutputInformation(file_key="input1", path="resource/input_files/input_file1.txt")
            f1.relation_file_or_tableioinfo_to_typeio = input_entry

            t1 = TableInputOutputInformation(model_py_path="FooBase", table_key="FooBase", table_name="FooBase")
            t1.set_table(FooBase)
            t1.relation_file_or_tableioinfo_to_typeio = output_entry
            timestamp_millis, timestamp_human = get_current_time()
            modification_table_entry = TableModificationTime(mtime_epoch_millis=timestamp_millis, table_name=t1.table_name)
            t1.modification = modification_table_entry

            o1 = Option(name="rows", value="1000")

            tw1 = Add(rule_name="rule1")
            tw1.relation_toolwrapper_to_fileioinfo.append(f1)
            tw1.relation_toolwrapper_to_tableioinfo.append(t1)
            tw1.relation_toolwrapper_to_option.append(o1)

            f12 = FileInputOutputInformation(file_key="input1", path="resource/input_files/input_file1.txt")
            f12.relation_file_or_tableioinfo_to_typeio = input_entry

            t12 = TableInputOutputInformation(model_py_path="FooBase", table_key="FooBase", table_name="FooBase")
            t12.set_table(FooBase)
            t12.relation_file_or_tableioinfo_to_typeio = output_entry
            timestamp_millis, timestamp_human = get_current_time()
            modification_table_entry = TableModificationTime(mtime_epoch_millis=timestamp_millis,
                                                             table_name=t12.table_name)
            t12.modification = modification_table_entry

            o12 = Option(name="rows", value="1000")

            tw12 = Add(rule_name="rule1")
            tw12.relation_toolwrapper_to_fileioinfo.append(f12)
            tw12.relation_toolwrapper_to_tableioinfo.append(t12)
            tw12.relation_toolwrapper_to_option.append(o12)

            f13 = FileInputOutputInformation(file_key="input1", path="resource/input_files/input_file1.txt")
            f13.relation_file_or_tableioinfo_to_typeio = input_entry

            t13 = TableInputOutputInformation(model_py_path="FooBase", table_key="FooBase", table_name="FooBase")
            t13.set_table(FooBase)
            t13.relation_file_or_tableioinfo_to_typeio = output_entry
            timestamp_millis, timestamp_human = get_current_time()
            modification_table_entry = TableModificationTime(mtime_epoch_millis=timestamp_millis,
                                                             table_name=t13.table_name)
            t13.modification = modification_table_entry

            o13 = Option(name="rows", value="1000")

            tw13 = Add(rule_name="rule1")
            tw13.relation_toolwrapper_to_fileioinfo.append(f13)
            tw13.relation_toolwrapper_to_tableioinfo.append(t13)
            tw13.relation_toolwrapper_to_option.append(o13)

            tt1 = ToolWrapperThread(tw1)
            tt2 = ToolWrapperThread(tw12)
            tt3 = ToolWrapperThread(tw13)

            t21 = TableInputOutputInformation(model_py_path="FooBase", table_key="FooBase", table_name="FooBase")
            t21.set_table(FooBase)
            t21.relation_file_or_tableioinfo_to_typeio = input_entry

            tw21 = Query(rule_name="rule1")
            tw21.relation_toolwrapper_to_tableioinfo.append(t21)

            t22 = TableInputOutputInformation(model_py_path="FooBase", table_key="FooBase", table_name="FooBase")
            t22.set_table(FooBase)
            t22.relation_file_or_tableioinfo_to_typeio = input_entry

            tw22 = Query(rule_name="rule1")
            tw22.relation_toolwrapper_to_tableioinfo.append(t22)

            t23 = TableInputOutputInformation(model_py_path="FooBase", table_key="FooBase", table_name="FooBase")
            t23.set_table(FooBase)
            t23.relation_file_or_tableioinfo_to_typeio = input_entry

            tw23 = Query(rule_name="rule1")
            tw23.relation_toolwrapper_to_tableioinfo.append(t23)

            tt4 = ToolWrapperThread(tw21)
            tt5 = ToolWrapperThread(tw22)
            tt6 = ToolWrapperThread(tw23)

            tt4.start()

            tt1.start()
            tt2.start()
            tt3.start()
            time.sleep(5)
            tt5.start()
            tt6.start()

            tt1.join()
            tt2.join()
            tt3.join()
            tt4.join()
            tt5.join()
            tt6.join()

    def tearDown(self):
        SQLManager.instance().get_session().close()
        SQLManager.instance().drop_all()
        shutil.rmtree("wopmars/tests/outdir", ignore_errors=True)

if __name__ == '__main__':
    unittest.main()
