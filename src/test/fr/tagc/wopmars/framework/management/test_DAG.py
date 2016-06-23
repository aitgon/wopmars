import unittest
from unittest import TestCase

from sqlalchemy.orm.session import make_transient

from FooWrapper2 import FooWrapper2
from FooWrapper8 import FooWrapper8
from src.main.fr.tagc.wopmars.framework.bdd.SQLManager import SQLManager
from src.main.fr.tagc.wopmars.framework.bdd.tables.IOFilePut import IOFilePut
from src.main.fr.tagc.wopmars.framework.bdd.tables.Option import Option

from src.main.fr.tagc.wopmars.framework.bdd.tables.ToolWrapper import ToolWrapper
from src.main.fr.tagc.wopmars.framework.bdd.tables.Type import Type
from src.main.fr.tagc.wopmars.framework.management.DAG import DAG
from src.main.fr.tagc.wopmars.utils.OptionManager import OptionManager


class TestDAG(TestCase):

    def setUp(self):
        OptionManager.initial_test_setup()
        SQLManager.create_all()
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

    def tearDown(self):
        SQLManager.drop_all()
        OptionManager._drop()
        SQLManager._drop()

    def test_init(self):
        try:
            my_dag = DAG(self.__set_tool)

            dag_from_base = DAG(set(SQLManager.instance().get_session().query(ToolWrapper).all()))
            self.assertEqual(my_dag, dag_from_base)
            # todo download un set a partir de la bdd

            # Verifying that the nodes are correctly sorted
            self.assertTrue(self.__toolwrapper_fourth in my_dag.successors(self.__toolwrapper_third))
            self.assertTrue(self.__toolwrapper_fourth in my_dag.successors(self.__toolwrapper_second))
            self.assertTrue(self.__toolwrapper_second in my_dag.successors(self.__toolwrapper_first))
            self.assertTrue(self.__toolwrapper_third in my_dag.successors(self.__toolwrapper_first))
        except:
            # beware, if a test inside the try block fails, 2 exceptions are raised
            raise AssertionError('Should not raise exception')

if __name__ == '__main__':
    unittest.main()

