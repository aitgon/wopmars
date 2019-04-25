import unittest
from unittest import TestCase

from test.resource.wrapper.FooWrapper2 import FooWrapper2
from test.resource.wrapper.FooWrapper8 import FooWrapper8
from wopmars.framework.database.SQLManager import SQLManager
from wopmars.framework.database.tables.IOFilePut import IOFilePut
from wopmars.framework.database.tables.ToolWrapper import ToolWrapper
from wopmars.framework.database.tables.Type import Type
from wopmars.framework.management.DAG import DAG
from wopmars.utils.OptionManager import OptionManager
from wopmars.utils.PathFinder import PathFinder


class TestDAG(TestCase):

    def setUp(self):
        OptionManager.initial_test_setup()
        SQLManager.instance().create_all()
        #        first
        #       /    \
        #   second   third
        #       \    /
        #       fourth
        #

        self.__session = SQLManager.instance().get_session()

        input_entry = Type(name="input")
        output_entry = Type(name="output")

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

        f1 = IOFilePut(name="input1", path="file2.txt")
        f1.type = input_entry

        f2 = IOFilePut(name="output1", path="file4.txt")
        f2.type = output_entry

        self.__toolwrapper_third = FooWrapper2(rule_name="rule3")
        self.__toolwrapper_third.files.extend([f1, f2])

        f1 = IOFilePut(name="input1", path="file3.txt")
        f1.type = input_entry

        f2 = IOFilePut(name="input2", path="file4.txt")
        f2.type = input_entry

        f3 = IOFilePut(name="output1", path="file5.txt")
        f3.type = output_entry

        self.__toolwrapper_fourth = FooWrapper8(rule_name="rule4")
        self.__toolwrapper_fourth.files.extend([f1, f2, f3])

        list_tool = [self.__toolwrapper_first,
                     self.__toolwrapper_second,
                     self.__toolwrapper_third,
                     self.__toolwrapper_fourth]

        self.__set_tool = set(list_tool)

        SQLManager.instance().get_session().add_all(list_tool)
        SQLManager.instance().get_session().commit()

    def test_get_all_successors(self):
        my_dag = DAG(self.__set_tool)

        self.assertEqual(set(my_dag.get_all_successors(self.__toolwrapper_first)), self.__set_tool)
        self.assertNotEqual(set(my_dag.get_all_successors(self.__toolwrapper_first)),
                            self.__set_tool.difference(set([self.__toolwrapper_second])))
        self.assertNotEqual(set(my_dag.get_all_successors(self.__toolwrapper_first)),
                            self.__set_tool.difference(set([self.__toolwrapper_first])))

    def test_get_all_predecessors(self):
        my_dag = DAG(self.__set_tool)

        self.assertEqual(set(my_dag.get_all_predecessors(self.__toolwrapper_fourth)), self.__set_tool)
        self.assertNotEqual(set(my_dag.get_all_predecessors(self.__toolwrapper_fourth)),
                            self.__set_tool.difference(set([self.__toolwrapper_second])))
        self.assertNotEqual(set(my_dag.get_all_predecessors(self.__toolwrapper_fourth)),
                            self.__set_tool.difference(set([self.__toolwrapper_fourth])))

    def tearDown(self):
        SQLManager.instance().get_session().close() 
        SQLManager.instance().drop_all()
        OptionManager._drop()
        PathFinder.silentremove("test/output/output_file1.txt")
        SQLManager._drop()

    def test_init(self):
        try:
            my_dag = DAG(self.__set_tool)

            dag_from_base = DAG(set(SQLManager.instance().get_session().query(ToolWrapper).all()))
            self.assertEqual(my_dag, dag_from_base)

            # Verifying that the nodes are correctly sorted
            self.assertTrue(self.__toolwrapper_fourth in my_dag.successors(self.__toolwrapper_third))
            self.assertTrue(self.__toolwrapper_fourth in my_dag.successors(self.__toolwrapper_second))
            self.assertTrue(self.__toolwrapper_second in my_dag.successors(self.__toolwrapper_first))
            self.assertTrue(self.__toolwrapper_third in my_dag.successors(self.__toolwrapper_first))
        except:
            # beware, if a test_bak inside the try block fails, 2 exceptions are raised
            raise AssertionError('Should not raise exception')

if __name__ == '__main__':
    unittest.main()

