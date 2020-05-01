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
from wopmars.tests.resource.wrapper.fooPackage.FooWrapperPackaged import FooWrapperPackaged
from wopmars.SQLManager import SQLManager
from wopmars.models.TableInputOutputInformation import TableInputOutputInformation
from wopmars.models.FileInputOutputInformation import FileInputOutputInformation
from wopmars.models.ToolWrapper import ToolWrapper
from wopmars.models.TypeInputOrOutput import TypeInputOrOutput
from wopmars.Reader import Reader
from wopmars.utils.OptionManager import OptionManager
from wopmars.utils.PathManager import PathManager
from wopmars.utils.SetUtils import SetUtils
from wopmars.utils.WopMarsException import WopMarsException


class TestReader(TestCase):

    def setUp(self):

        OptionManager.initial_test_setup()  # Set tests arguments
        SQLManager.instance().create_all()  # Create database with tables

        session = SQLManager.instance().get_session()
        session.get_or_create(TypeInputOrOutput, defaults={"is_input": True}, is_input=True)
        session.get_or_create(TypeInputOrOutput, defaults={"is_input": False}, is_input=False)
        session.commit()
        self.__session = SQLManager.instance().get_session()
        self.__reader = Reader()

        self.__testdir_path = PathManager.get_test_path()

        # The good -------------------------------:

        self.__example_def_file1_path = os.path.join(self.__testdir_path, "resource/wopfile/example_def_file1.yml")
        self.__example_def_file3_path = os.path.join(self.__testdir_path, "resource/wopfile/example_def_file3.yml")

        # The ugly (malformed file) --------------------:

        self.__s_example_definition_file_duplicate_rule = os.path.join(self.__testdir_path, "resource/wopfile/example_def_file_duplicate_rule.yml")

        self.__list_f_to_exception_init = [
            os.path.join(self.__testdir_path, s_path) for s_path in [
                "resource/wopfile/example_def_file_wrong_yaml.yml",
                "resource/wopfile/example_def_file_duplicate_rule.yml",
                "resource/wopfile/example_def_file_wrong_grammar.yml",
                "resource/wopfile/example_def_file_wrong_grammar2.yml",
                "resource/wopfile/example_def_file_wrong_grammar3.yml",
                "resource/wopfile/example_def_file_wrong_grammar4.yml"
                ]
        ]

        # The bad (invalid file) ----------------------:

        self.__list_s_to_exception_read = [
            os.path.join(self.__testdir_path, s_path) for s_path in [
                "resource/wopfile/example_def_file1.yml",
                "resource/wopfile/example_def_file_wrong_content2.yml",
                "resource/wopfile/example_def_file_wrong_content3.yml",
                "resource/wopfile/example_def_file_wrong_content4.yml",
                "resource/wopfile/example_def_file_wrong_content5.yml",
                "resource/wopfile/example_def_file_wrong_class_name.yml",
                "resource/wopfile/example_def_file_wrong_rule.yml",
            ]
        ]

    # Fix this tests for Travis
    # def test_load_definition_file(self):
    #     for file in self.__list_f_to_exception_init:
    #         with self.assertRaises(WopMarsException):
    #             self.__reader.load_wopfile_as_yml_dic(file)
    #     # Not existing file
    #     with self.assertRaises(WopMarsException):
    #         self.__reader.load_wopfile_as_yml_dic("Not existing file.")

    def test_check_duplicate_rule(self):
        with open(self.__s_example_definition_file_duplicate_rule) as file_duplicate_rule:
            with self.assertRaises(WopMarsException):
                Reader.check_duplicate_rules(file_duplicate_rule.read())

        with open(self.__example_def_file1_path) as file:
            try:
                Reader.check_duplicate_rules(file.read())
            except Exception as e:
                raise AssertionError("Should not raise an exception " + str(e))

    def test_read2(self):
        try:
            self.__reader.iterate_wopfile_yml_dic_and_insert_rules_in_db(self.__example_def_file3_path)
            result = self.__session.query(ToolWrapper).one()
        except:
            raise AssertionError("Packaged wrappers should not raise an exception")

        input_entry = TypeInputOrOutput(is_input=True)
        output_entry = TypeInputOrOutput(is_input=False)

        f1 = FileInputOutputInformation(file_key="input1", path="resource/input_files/input_file1.txt")
        f1.relation_file_or_tableioinfo_to_typeio = input_entry

        f2 = FileInputOutputInformation(file_key="output1", path="outdir/output_file1.txt")
        f2.relation_file_or_tableioinfo_to_typeio = output_entry

        t1 = TableInputOutputInformation(model_py_path="resource.model.fooPackage.FooBasePackaged",
                                         table_key="FooBasePackaged", table_name="FooBasePackaged")
        t1.relation_file_or_tableioinfo_to_typeio = input_entry

        tw1 = FooWrapperPackaged(rule_name="rule1")
        tw1.relation_toolwrapper_to_fileioinfo.extend([f1, f2])
        tw1.relation_toolwrapper_to_tableioinfo.append(t1)

        self.assertEqual(result, tw1)

    def test_read(self):

        self.__reader.iterate_wopfile_yml_dic_and_insert_rules_in_db(self.__example_def_file1_path)
        result = set(self.__session.query(ToolWrapper).all())

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

        expected = set([tw1, tw2, tw3, tw4, tw5, tw6, tw7])

        # The good ------------------------------------:
        self.assertTrue((SetUtils.all_elm_of_one_set_in_one_other(result, expected) and
                         SetUtils.all_elm_of_one_set_in_one_other(expected, result)))

        # The bad -------------------------------------:

        # [self.assertRaises(WopMarsException, self.__reader.iterate_wopfile_yml_dic_and_insert_rules_in_db, file) for file in self.__list_s_to_exception_read]

        SQLManager.instance().get_session().rollback()

    def tearDown(self):
        SQLManager.instance().get_session().close()
        SQLManager.instance().drop_all()
        OptionManager._drop()
        SQLManager._drop()
        shutil.rmtree(os.path.join(self.__testdir_path, "outdir"), ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
