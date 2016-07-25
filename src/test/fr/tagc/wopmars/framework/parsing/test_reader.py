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
from fooPackage.FooWrapperPackaged import FooWrapperPackaged
from src.main.fr.tagc.wopmars.framework.bdd.SQLManager import SQLManager
from src.main.fr.tagc.wopmars.framework.bdd.tables.IODbPut import IODbPut
from src.main.fr.tagc.wopmars.framework.bdd.tables.IOFilePut import IOFilePut

from FooWrapper1 import FooWrapper1
from FooWrapper2 import FooWrapper2
from FooWrapper3 import FooWrapper3
from src.main.fr.tagc.wopmars.framework.bdd.tables.Option import Option
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
        session = SQLManager.instance().get_session()
        session.get_or_create(Type, defaults={"id": 1}, name="input")
        session.get_or_create(Type, defaults={"id": 2}, name="output")
        session.commit()
        self.__session = SQLManager.instance().get_session()
        self.__reader = Reader()

        s_root_path = PathFinder.find_src(os.path.dirname(os.path.realpath(__file__)))

        # The good -------------------------------:

        self.__s_example_definition_file = s_root_path + "resources/example_def_file.yml"
        self.__s_example_definition_file2 = s_root_path + "resources/example_def_file3.yml"

        # The ugly (malformed file) --------------------:

        self.__s_example_definition_file_duplicate_rule = s_root_path + "resources/example_def_file_duplicate_rule.yml"

        self.__list_f_to_exception_init = [
            s_root_path + s_path for s_path in [
                "resources/example_def_file_wrong_yaml.yml",
                "resources/example_def_file_duplicate_rule.yml",
                "resources/example_def_file_wrong_grammar.yml",
                "resources/example_def_file_wrong_grammar2.yml",
                "resources/example_def_file_wrong_grammar3.yml",
                "resources/example_def_file_wrong_grammar4.yml"
                ]
        ]

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

    def test_load_definition_file(self):
        [self.assertRaises(WopMarsException, self.__reader.load_definition_file, file) for file in self.__list_f_to_exception_init]

        # Not existing file
        with self.assertRaises(WopMarsException):
            self.__reader.load_definition_file("Not existing file.")

    def tearDown(self):
        SQLManager.instance().drop_all()
        PathFinder.dir_content_remove("resources/outputs/")
        OptionManager._drop()
        SQLManager._drop()

    def test_check_duplicate_rule(self):
        with open(self.__s_example_definition_file_duplicate_rule) as file_duplicate_rule:
            with self.assertRaises(WopMarsException):
                Reader.check_duplicate_rules(file_duplicate_rule.read())

        with open(self.__s_example_definition_file) as file:
            try:
                Reader.check_duplicate_rules(file.read())
            except Exception as e:
                raise AssertionError("Should not raise an exception " + str(e))

    def test_read2(self):
        try:
            self.__reader.read(self.__s_example_definition_file2)
            result = self.__session.query(ToolWrapper).one()
        except:
            raise AssertionError("Packaged wrappers should not raise an exception")

        input_entry = Type(name="input")
        output_entry = Type(name="output")

        f1 = IOFilePut(name="input1", path="resources/input_File1.txt")
        f1.type = input_entry

        f2 = IOFilePut(name="output1", path="resources/outputs/output_File1.txt")
        f2.type = output_entry

        t1 = IODbPut(model="fooPackage.FooBasePackaged", tablename="FooBasePackaged")
        t1.type = input_entry

        tw1 = FooWrapperPackaged(rule_name="rule1")
        tw1.files.extend([f1, f2])
        tw1.tables.append(t1)

        self.assertEqual(result, tw1)

    def test_read(self):

        self.__reader.read(self.__s_example_definition_file)
        result = set(self.__session.query(ToolWrapper).all())

        input_entry = Type(name="input")
        output_entry = Type(name="output")

        f1 = IOFilePut(name="input1", path="resources/input_File1.txt")
        f1.type = input_entry

        f2 = IOFilePut(name="output1", path="resources/outputs/output_File1.txt")
        f2.type = output_entry

        f3 = IOFilePut(name="input1", path="resources/outputs/output_File1.txt")
        f3.type = input_entry

        f3bis = IOFilePut(name="input1", path="resources/outputs/output_File1.txt")
        f3bis.type = input_entry

        f4 = IOFilePut(name="output1", path="resources/outputs/output_File2.txt")
        f4.type = output_entry

        f5 = IOFilePut(name="output1", path="resources/outputs/output_File3.txt")
        f5.type = output_entry

        f6 = IOFilePut(name="output2", path="resources/outputs/output_File4.txt")
        f6.type = output_entry

        f7 = IOFilePut(name="input1", path="resources/outputs/output_File3.txt")
        f7.type = input_entry

        f8 = IOFilePut(name="input2", path="resources/outputs/output_File2.txt")
        f8.type = input_entry

        f9 = IOFilePut(name="output1", path="resources/outputs/output_File5.txt")
        f9.type = output_entry

        f10 = IOFilePut(name="input1", path="resources/outputs/output_File4.txt")
        f10.type = input_entry

        f11 = IOFilePut(name="output1", path="resources/outputs/output_File6.txt")
        f11.type = output_entry

        f12 = IOFilePut(name="input1", path="resources/outputs/output_File1.txt")
        f12.type = input_entry

        f13 = IOFilePut(name="input2", path="resources/outputs/output_File5.txt")
        f13.type = input_entry

        f14 = IOFilePut(name="input3", path="resources/outputs/output_File6.txt")
        f14.type = input_entry

        f15 = IOFilePut(name="output1", path="resources/outputs/output_File7.txt")
        f15.type = output_entry

        t1 = IODbPut(model="FooBase", tablename="FooBase")
        t1.type = output_entry

        t1bis = IODbPut(model="FooBase", tablename="FooBase")
        t1bis.type = input_entry

        t2 = IODbPut(model="FooBase2", tablename="FooBase2")
        t2.type = output_entry

        t2bis = IODbPut(model="FooBase2", tablename="FooBase2")
        t2bis.type = input_entry

        tw1 = FooWrapper4(rule_name="rule1")
        tw1.files.extend([f1, f2])
        tw2 = FooWrapper5(rule_name="rule2")
        tw2.files.extend([f3, f4])
        tw2.tables.extend([t1])
        tw3 = FooWrapper6(rule_name="rule3")
        tw3.files.extend([f3bis, f5, f6])
        tw4 = FooWrapper7(rule_name="rule4")
        tw4.tables.extend([t1bis, t2])
        tw5 = FooWrapper8(rule_name="rule5")
        tw5.files.extend([f8, f7, f9])
        tw6 = FooWrapper9(rule_name="rule6")
        tw6.files.extend([f10, f11])
        tw6.tables.extend([t2bis])
        tw7 = FooWrapper10(rule_name="rule7")
        tw7.files.extend([f12, f13, f14, f15])

        expected = set([tw1, tw2, tw3, tw4, tw5, tw6, tw7])

        # The good ------------------------------------:

        self.assertTrue((SetUtils.all_elm_of_one_set_in_one_other(result, expected) and
                         SetUtils.all_elm_of_one_set_in_one_other(expected, result)))

        # The bad -------------------------------------:

        [self.assertRaises(WopMarsException, self.__reader.read, file) for file in self.__list_s_to_exception_read]

        SQLManager.instance().get_session().rollback()


if __name__ == "__main__":
    unittest.main()