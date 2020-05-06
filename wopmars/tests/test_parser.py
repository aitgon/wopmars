import os
import shutil
import unittest
from unittest import TestCase

from wopmars.tests.resource.wrapper.FooWrapper10 import FooWrapper10
from wopmars.tests.resource.wrapper.FooWrapper4 import FooWrapper4
from wopmars.tests.resource.wrapper.FooWrapper5 import FooWrapper5
from wopmars.tests.resource.wrapper.FooWrapper6 import FooWrapper6
from wopmars.tests.resource.wrapper.FooWrapper7 import FooWrapper7
from wopmars.tests.resource.wrapper.FooWrapper8 import FooWrapper8
from wopmars.tests.resource.wrapper.FooWrapper9 import FooWrapper9
from wopmars.SQLManager import SQLManager
from wopmars.models.TableInputOutputInformation import TableInputOutputInformation
from wopmars.models.FileInputOutputInformation import FileInputOutputInformation
from wopmars.models.TypeInputOrOutput import TypeInputOrOutput
from wopmars.DAG import DAG
from wopmars.Parser import Parser
from wopmars.utils.OptionManager import OptionManager
from wopmars.utils.PathManager import PathManager
from wopmars.utils.WopMarsException import WopMarsException


class TestParser(TestCase):

    def setUp(self):
        OptionManager.initial_test_setup()  # Set tests arguments
        SQLManager.instance().create_all()  # Create database with tables
        session = SQLManager.instance().get_session()
        session.get_or_create(TypeInputOrOutput, defaults={"is_input": True}, is_input=True)
        session.get_or_create(TypeInputOrOutput, defaults={"is_input": False}, is_input=False)
        session.commit()
        self.__test_path = PathManager.get_test_path()
        # self.__test_path = PathManager.get_package_path()
        self.__parser = Parser()

    def tearDown(self):
        SQLManager.instance().get_session().close()
        SQLManager.instance().drop_all()
        # PathManager.dir_content_remove("outdir")
        shutil.rmtree("outdir", ignore_errors=True)
        OptionManager._drop()
        SQLManager._drop()

    def test_parse(self):
        OptionManager.initial_test_setup()

        # The good --------------------------:
        input_entry = TypeInputOrOutput(is_input=True)
        output_entry = TypeInputOrOutput(is_input=False)

        f1 = FileInputOutputInformation(file_key="input1", path="resource/input_files/input_file1.txt")
        f1.relation_file_or_tableioinfo_to_typeio = input_entry

        f2 = FileInputOutputInformation(file_key="output1", path="outdir/output_file1.txt")
        f2.relation_file_or_tableioinfo_to_typeio = output_entry

        f3 = FileInputOutputInformation(file_key="input1", path="outdir/output_file1.txt")
        f3.relation_file_or_tableioinfo_to_typeio = input_entry

        f3bis = FileInputOutputInformation(file_key="input1", path="outdir/output_file1.txt")
        f3bis.relation_file_or_tableioinfo_to_typeio = input_entry

        f4 = FileInputOutputInformation(file_key="output1", path="outdir/output_file2.txt")
        f4.relation_file_or_tableioinfo_to_typeio = output_entry

        f5 = FileInputOutputInformation(file_key="output1", path="outdir/output_file3.txt")
        f5.relation_file_or_tableioinfo_to_typeio = output_entry

        f6 = FileInputOutputInformation(file_key="output2", path="outdir/output_file4.txt")
        f6.relation_file_or_tableioinfo_to_typeio = output_entry

        f7 = FileInputOutputInformation(file_key="input1", path="outdir/output_file3.txt")
        f7.relation_file_or_tableioinfo_to_typeio = input_entry

        f8 = FileInputOutputInformation(file_key="input2", path="outdir/output_file2.txt")
        f8.relation_file_or_tableioinfo_to_typeio = input_entry

        f9 = FileInputOutputInformation(file_key="output1", path="outdir/output_file5.txt")
        f9.relation_file_or_tableioinfo_to_typeio = output_entry

        f10 = FileInputOutputInformation(file_key="input1", path="outdir/output_file4.txt")
        f10.relation_file_or_tableioinfo_to_typeio = input_entry

        f11 = FileInputOutputInformation(file_key="output1", path="outdir/output_file6.txt")
        f11.relation_file_or_tableioinfo_to_typeio = output_entry

        f12 = FileInputOutputInformation(file_key="input1", path="outdir/output_file1.txt")
        f12.relation_file_or_tableioinfo_to_typeio = input_entry

        f13 = FileInputOutputInformation(file_key="input2", path="outdir/output_file5.txt")
        f13.relation_file_or_tableioinfo_to_typeio = input_entry

        f14 = FileInputOutputInformation(file_key="input3", path="outdir/output_file6.txt")
        f14.relation_file_or_tableioinfo_to_typeio = input_entry

        f15 = FileInputOutputInformation(file_key="output1", path="outdir/output_file7.txt")
        f15.relation_file_or_tableioinfo_to_typeio = output_entry

        t1 = TableInputOutputInformation(model_py_path="FooBase", table_key="FooBase", table_name="FooBase")
        t1.relation_file_or_tableioinfo_to_typeio = output_entry

        t1bis = TableInputOutputInformation(model_py_path="FooBase", table_key="FooBase", table_name="FooBase")
        t1bis.relation_file_or_tableioinfo_to_typeio = input_entry

        t2 = TableInputOutputInformation(model_py_path="FooBase2", table_key="FooBase2", table_name="FooBase2")
        t2.relation_file_or_tableioinfo_to_typeio = output_entry

        t2bis = TableInputOutputInformation(model_py_path="FooBase2", table_key="FooBase2", table_name="FooBase2")
        t2bis.relation_file_or_tableioinfo_to_typeio = input_entry

        tw1 = FooWrapper4(rule_name="rule1")
        tw1.relation_toolwrapper_to_fileioinfo.extend([f1, f2])
        tw2 = FooWrapper5(rule_name="rule2")
        tw2.relation_toolwrapper_to_fileioinfo.extend([f3, f4])
        tw2.relation_toolwrapper_to_tableioinfo.extend([t1])
        tw3 = FooWrapper6(rule_name="rule3")
        tw3.relation_toolwrapper_to_fileioinfo.extend([f3bis, f5, f6])
        tw4 = FooWrapper7(rule_name="rule4")
        tw4.relation_toolwrapper_to_tableioinfo.extend([t1bis, t2])
        tw5 = FooWrapper8(rule_name="rule5")
        tw5.relation_toolwrapper_to_fileioinfo.extend([f8, f7, f9])
        tw6 = FooWrapper9(rule_name="rule6")
        tw6.relation_toolwrapper_to_fileioinfo.extend([f10, f11])
        tw6.relation_toolwrapper_to_tableioinfo.extend([t2bis])
        tw7 = FooWrapper10(rule_name="rule7")
        tw7.relation_toolwrapper_to_fileioinfo.extend([f12, f13, f14, f15])

        set_toolwrappers = set([tw1, tw2, tw3, tw4, tw5, tw6, tw7])

        OptionManager.instance()["--dot"] = None

        dag_expected = DAG(set_toolwrappers)
        OptionManager.instance()["--wopfile"] = os.path.join(self.__test_path, "resource/wopfile/example_def_file1.yml")
        dag_obtained = self.__parser.parse()
        self.assertEqual(dag_expected, dag_obtained)

        OptionManager.instance()["--wopfile"] = os.path.join(self.__test_path, "resource/wopfile/example_def_file_not_a_dag.yml")
        with self.assertRaises(WopMarsException):
            self.__parser.parse()

        # Verify the dot file ----------------:
        OptionManager.instance()["--wopfile"] = os.path.join(self.__test_path, "resource/wopfile/example_def_file1.yml")
        #dot_path = os.path.join(self.__package_path, "test_bak.dot")
        #OptionManager.instance()["--dot"] = dot_path
        self.__parser.parse()
        #self.assertTrue(os.path.isfile(dot_path))
        #os.remove(dot_path)
        #os.remove(dot_path[:-4] + ".ps")

if __name__ == '__main__':
    unittest.main()
