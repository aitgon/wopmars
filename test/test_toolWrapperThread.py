import time
import unittest
from unittest import TestCase

from test.resource.model.FooBase import FooBase
from test.resource.wrapper.FooWrapper5 import FooWrapper5
from test.resource.wrapper.sprintFive.Add import Add as tw_add
from test.resource.wrapper.sprintFive.Query import Query as tw_query
from wopmars.SQLManager import SQLManager
from wopmars.models.TableInputOutputInformation import TableInputOutputInformation
from wopmars.models.FileInputOutputInformation import FileInputOutputInformation
from wopmars.models.TableModificationTime import TableModificationTime
from wopmars.models.Option import Option
from wopmars.models.TypeInputOrOutput import TypeInputOrOutput
from wopmars.ToolWrapperThread import ToolWrapperThread
from wopmars.utils.OptionManager import OptionManager
from wopmars.utils.PathFinder import PathFinder
from wopmars.utils.various import get_current_time


class TestToolWrapperThread(TestCase):

    def setUp(self):
        OptionManager.initial_test_setup()
        SQLManager.instance().create_all()

        [SQLManager.instance().get_session().add(FooBase(name="foo " + str(i))) for i in range(10000)]
        SQLManager.instance().get_session().commit()

    def test_run(self):

        input_entry = TypeInputOrOutput(is_input=True)
        output_entry = TypeInputOrOutput(is_input=False)

        f1 = FileInputOutputInformation(name="input1", path="test/resource/input_files/input_file1.txt")
        f1.relation_typeio_to_file_or_tableioinfo = input_entry

        f2 = FileInputOutputInformation(name="output1", path="test/output/output_file1.txt")
        f2.relation_typeio_to_file_or_tableioinfo = output_entry

        t1 = TableInputOutputInformation(model_py_path="FooBase", table_name="FooBase")
        t1.set_table(FooBase)
        t1.relation_typeio_to_file_or_tableioinfo = output_entry
        timestamp_millis, timestamp_human = get_current_time()
        modification_table_entry = TableModificationTime(mtime_epoch_millis=timestamp_millis, table_name=t1.table_name)
        t1.modification = modification_table_entry

        tw1 = FooWrapper5(rule_name="rule1")
        tw1.relation_typeio_to_fileioinfo.extend([f1, f2])
        tw1.relation_typeio_to_tableioinfo.append(t1)

        f12 = FileInputOutputInformation(name="input1", path="test/resource/input_files/input_file1.txt")
        f12.relation_typeio_to_file_or_tableioinfo = input_entry

        f22 = FileInputOutputInformation(name="output1", path="test/output/output_file1.txt")
        f22.relation_typeio_to_file_or_tableioinfo = output_entry

        t12 = TableInputOutputInformation(model_py_path="FooBase", table_name="FooBase")
        t12.set_table(FooBase)
        t12.relation_typeio_to_file_or_tableioinfo = output_entry
        timestamp_millis, timestamp_human = get_current_time()
        modification_table_entry = TableModificationTime(
            mtime_epoch_millis=timestamp_millis, table_name=t12.table_name)
        t12.modification = modification_table_entry

        tw2 = FooWrapper5(rule_name="rule2")
        tw2.relation_typeio_to_fileioinfo.extend([f12, f22])
        tw2.relation_typeio_to_tableioinfo.append(t12)

        f13 = FileInputOutputInformation(name="input1", path="test/resource/input_files/input_file1.txt")
        f13.relation_typeio_to_file_or_tableioinfo = input_entry

        f23 = FileInputOutputInformation(name="output1", path="test/output/output_file1.txt")
        f23.relation_typeio_to_file_or_tableioinfo = output_entry

        t13 = TableInputOutputInformation(model_py_path="FooBase", table_name="FooBase")
        t13.set_table(FooBase)
        t13.relation_typeio_to_file_or_tableioinfo = output_entry
        timestamp_millis, timestamp_human = get_current_time()
        modification_table_entry = TableModificationTime(
            mtime_epoch_millis=timestamp_millis, table_name=t13.table_name)
        t13.modification = modification_table_entry

        tw3 = FooWrapper5(rule_name="rule3")
        tw3.relation_typeio_to_fileioinfo.extend([f13, f23])
        tw3.relation_typeio_to_tableioinfo.append(t13)

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
        # this test does not work with mysql and postgresql
        if not SQLManager.instance().engine.url.drivername in ['mysql', 'postgresql']:
            input_entry = TypeInputOrOutput(is_input=True)
            output_entry = TypeInputOrOutput(is_input=False)

            f1 = FileInputOutputInformation(name="input1", path="test/resource/input_files/input_file1.txt")
            f1.relation_typeio_to_file_or_tableioinfo = input_entry

            t1 = TableInputOutputInformation(model_py_path="FooBase", table_name="FooBase")
            t1.set_table(FooBase)
            t1.relation_typeio_to_file_or_tableioinfo = output_entry
            timestamp_millis, timestamp_human = get_current_time()
            modification_table_entry = TableModificationTime(mtime_epoch_millis=timestamp_millis, table_name=t1.table_name)
            t1.modification = modification_table_entry

            o1 = Option(name="rows", value="1000")

            tw1 = tw_add(rule_name="rule1")
            tw1.relation_typeio_to_fileioinfo.append(f1)
            tw1.relation_typeio_to_tableioinfo.append(t1)
            tw1.relation_toolwrapper_to_option.append(o1)

            f12 = FileInputOutputInformation(name="input1", path="test/resource/input_files/input_file1.txt")
            f12.relation_typeio_to_file_or_tableioinfo = input_entry

            t12 = TableInputOutputInformation(model_py_path="FooBase", table_name="FooBase")
            t12.set_table(FooBase)
            t12.relation_typeio_to_file_or_tableioinfo = output_entry
            timestamp_millis, timestamp_human = get_current_time()
            modification_table_entry = TableModificationTime(mtime_epoch_millis=timestamp_millis,
                                                             table_name=t12.table_name)
            t12.modification = modification_table_entry

            o12 = Option(name="rows", value="1000")

            tw12 = tw_add(rule_name="rule1")
            tw12.relation_typeio_to_fileioinfo.append(f12)
            tw12.relation_typeio_to_tableioinfo.append(t12)
            tw12.relation_toolwrapper_to_option.append(o12)

            f13 = FileInputOutputInformation(name="input1", path="test/resource/input_files/input_file1.txt")
            f13.relation_typeio_to_file_or_tableioinfo = input_entry

            t13 = TableInputOutputInformation(model_py_path="FooBase", table_name="FooBase")
            t13.set_table(FooBase)
            t13.relation_typeio_to_file_or_tableioinfo = output_entry
            timestamp_millis, timestamp_human = get_current_time()
            modification_table_entry = TableModificationTime(mtime_epoch_millis=timestamp_millis,
                                                             table_name=t13.table_name)
            t13.modification = modification_table_entry

            o13 = Option(name="rows", value="1000")

            tw13 = tw_add(rule_name="rule1")
            tw13.relation_typeio_to_fileioinfo.append(f13)
            tw13.relation_typeio_to_tableioinfo.append(t13)
            tw13.relation_toolwrapper_to_option.append(o13)

            tt1 = ToolWrapperThread(tw1)
            tt2 = ToolWrapperThread(tw12)
            tt3 = ToolWrapperThread(tw13)

            t21 = TableInputOutputInformation(model_py_path="FooBase", table_name="FooBase")
            t21.set_table(FooBase)
            t21.relation_typeio_to_file_or_tableioinfo = input_entry

            tw21 = tw_query(rule_name="rule1")
            tw21.relation_typeio_to_tableioinfo.append(t21)

            t22 = TableInputOutputInformation(model_py_path="FooBase", table_name="FooBase")
            t22.set_table(FooBase)
            t22.relation_typeio_to_file_or_tableioinfo = input_entry

            tw22 = tw_query(rule_name="rule1")
            tw22.relation_typeio_to_tableioinfo.append(t22)

            t23 = TableInputOutputInformation(model_py_path="FooBase", table_name="FooBase")
            t23.set_table(FooBase)
            t23.relation_typeio_to_file_or_tableioinfo = input_entry

            tw23 = tw_query(rule_name="rule1")
            tw23.relation_typeio_to_tableioinfo.append(t23)

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
        PathFinder.silentremove("test/output/")

if __name__ == '__main__':
    unittest.main()
