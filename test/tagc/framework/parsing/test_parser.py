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
from wopmars.main.tagc.framework.bdd.SQLManager import SQLManager
from wopmars.main.tagc.framework.bdd.tables.IODbPut import IODbPut
from wopmars.main.tagc.framework.bdd.tables.IOFilePut import IOFilePut
from wopmars.main.tagc.framework.bdd.tables.Type import Type
from wopmars.main.tagc.framework.management.DAG import DAG
from wopmars.main.tagc.framework.parsing.Parser import Parser
from wopmars.main.tagc.utils.OptionManager import OptionManager
from wopmars.main.tagc.utils.PathFinder import PathFinder
from wopmars.main.tagc.utils.exceptions.WopMarsException import WopMarsException


class TestParser(TestCase):
    def setUp(self):
        OptionManager.initial_test_setup()

        SQLManager.instance().create_all()
        session = SQLManager.instance().get_session()
        session.get_or_create(Type, defaults={"id": 1}, name="input")
        session.get_or_create(Type, defaults={"id": 2}, name="output")
        session.commit()
        self.__s_root_path = PathFinder.find_src(os.path.dirname(os.path.realpath(__file__)))
        self.__parser = Parser()

    def tearDown(self):
        SQLManager.instance().drop_all()
        PathFinder.dir_content_remove("resources/outputs/")
        OptionManager._drop()
        SQLManager._drop()

    def test_parse(self):
        OptionManager.initial_test_setup()

        # The good --------------------------:
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

        set_toolwrappers = set([tw1, tw2, tw3, tw4, tw5, tw6, tw7])

        OptionManager.instance()["--dot"] = None

        dag_expected = DAG(set_toolwrappers)
        OptionManager.instance()["--wopfile"] = self.__s_root_path + "resources/example_def_file.yml"
        dag_obtained = self.__parser.parse()

        self.assertEqual(dag_expected, dag_obtained)

        OptionManager.instance()["--wopfile"] = self.__s_root_path + "resources/example_def_file_not_a_dag.yml"
        with self.assertRaises(WopMarsException):
            self.__parser.parse()

        # Verify the dot file ----------------:
        OptionManager.instance()["--wopfile"] = self.__s_root_path + "resources/example_def_file.yml"
        dot_path = self.__s_root_path + "test_bak.dot"
        OptionManager.instance()["--dot"] = dot_path
        self.__parser.parse()
        self.assertTrue(os.path.isfile(dot_path))
        os.remove(dot_path)
        os.remove(dot_path[:-4] + ".ps")

if __name__ == '__main__':
    unittest.main()
