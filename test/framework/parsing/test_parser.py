import os
import unittest
from unittest import TestCase

from test.resource.wrapper.FooWrapper10 import FooWrapper10
from test.resource.wrapper.FooWrapper4 import FooWrapper4
from test.resource.wrapper.FooWrapper5 import FooWrapper5
from test.resource.wrapper.FooWrapper6 import FooWrapper6
from test.resource.wrapper.FooWrapper7 import FooWrapper7
from test.resource.wrapper.FooWrapper8 import FooWrapper8
from test.resource.wrapper.FooWrapper9 import FooWrapper9
from wopmars.framework.database.SQLManager import SQLManager
from wopmars.framework.database.tables.IODbPut import IODbPut
from wopmars.framework.database.tables.IOFilePut import IOFilePut
from wopmars.framework.database.tables.Type import Type
from wopmars.framework.management.DAG import DAG
from wopmars.framework.parsing.Parser import Parser
from wopmars.utils.OptionManager import OptionManager
from wopmars.utils.PathFinder import PathFinder
from wopmars.utils.exceptions.WopMarsException import WopMarsException


class TestParser(TestCase):
    def setUp(self):
        OptionManager.initial_test_setup()

        SQLManager.instance().create_all()
        session = SQLManager.instance().get_session()
        session.get_or_create(Type, defaults={"id": 1}, name="input")
        session.get_or_create(Type, defaults={"id": 2}, name="output")
        session.commit()
        self.__s_root_path = PathFinder.get_module_path()
        self.__parser = Parser()

    def tearDown(self):
        SQLManager.instance().get_session().close()
        SQLManager.instance().drop_all()
        PathFinder.dir_content_remove("test/output")
        OptionManager._drop()
        SQLManager._drop()

    def test_parse(self):
        OptionManager.initial_test_setup()

        # The good --------------------------:
        input_entry = Type(name="input")
        output_entry = Type(name="output")

        f1 = IOFilePut(name="input1", path="test/resource/input_files/input_file1.txt")
        f1.type = input_entry

        f2 = IOFilePut(name="output1", path="test/output/output_file1.txt")
        f2.type = output_entry

        f3 = IOFilePut(name="input1", path="test/output/output_file1.txt")
        f3.type = input_entry

        f3bis = IOFilePut(name="input1", path="test/output/output_file1.txt")
        f3bis.type = input_entry

        f4 = IOFilePut(name="output1", path="test/output/output_file2.txt")
        f4.type = output_entry

        f5 = IOFilePut(name="output1", path="test/output/output_file3.txt")
        f5.type = output_entry

        f6 = IOFilePut(name="output2", path="test/output/output_file4.txt")
        f6.type = output_entry

        f7 = IOFilePut(name="input1", path="test/output/output_file3.txt")
        f7.type = input_entry

        f8 = IOFilePut(name="input2", path="test/output/output_file2.txt")
        f8.type = input_entry

        f9 = IOFilePut(name="output1", path="test/output/output_file5.txt")
        f9.type = output_entry

        f10 = IOFilePut(name="input1", path="test/output/output_file4.txt")
        f10.type = input_entry

        f11 = IOFilePut(name="output1", path="test/output/output_file6.txt")
        f11.type = output_entry

        f12 = IOFilePut(name="input1", path="test/output/output_file1.txt")
        f12.type = input_entry

        f13 = IOFilePut(name="input2", path="test/output/output_file5.txt")
        f13.type = input_entry

        f14 = IOFilePut(name="input3", path="test/output/output_file6.txt")
        f14.type = input_entry

        f15 = IOFilePut(name="output1", path="test/output/output_file7.txt")
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
        OptionManager.instance()["--wopfile"] = os.path.join(self.__s_root_path, "test/resource/wopfile/example_def_file1.yml")
        dag_obtained = self.__parser.parse()
        self.assertEqual(dag_expected, dag_obtained)

        OptionManager.instance()["--wopfile"] = os.path.join(self.__s_root_path, "test/resource/wopfile/example_def_file_not_a_dag.yml")
        with self.assertRaises(WopMarsException):
            self.__parser.parse()

        # Verify the dot file ----------------:
        OptionManager.instance()["--wopfile"] = os.path.join(self.__s_root_path, "test/resource/wopfile/example_def_file1.yml")
        #dot_path = os.path.join(self.__s_root_path, "test_bak.dot")
        #OptionManager.instance()["--dot"] = dot_path
        self.__parser.parse()
        #self.assertTrue(os.path.isfile(dot_path))
        #os.remove(dot_path)
        #os.remove(dot_path[:-4] + ".ps")

if __name__ == '__main__':
    unittest.main()
