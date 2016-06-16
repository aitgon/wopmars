import unittest
from unittest import TestCase

from sqlalchemy.orm.session import make_transient

from FooWrapper2 import FooWrapper2
from FooWrapper8 import FooWrapper8
from src.main.fr.tagc.wopmars.framework.bdd.SQLManager import SQLManager
from src.main.fr.tagc.wopmars.framework.bdd.tables.IOFilePut import IOFilePut
from src.main.fr.tagc.wopmars.framework.bdd.tables.Option import Option
from src.main.fr.tagc.wopmars.framework.bdd.tables.RuleFile import RuleFile

from src.main.fr.tagc.wopmars.framework.bdd.tables.ToolWrapper import ToolWrapper
from src.main.fr.tagc.wopmars.framework.bdd.tables.Type import Type
from src.main.fr.tagc.wopmars.framework.management.DAG import DAG
from src.main.fr.tagc.wopmars.utils.OptionManager import OptionManager


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
        f2 = IOFilePut(name="output1", path="file2.txt")

        rf1 = RuleFile()
        rf1.type = input_entry
        rf1.file = f1

        rf2 = RuleFile()
        rf2.type = output_entry
        rf2.file = f2

        self.__toolwrapper_first = FooWrapper2(rule_name="rule1")
        self.__toolwrapper_first.files.extend([rf1, rf2])

        f3 = IOFilePut(name="input1", path="file2.txt")
        f4 = IOFilePut(name="output1", path="file3.txt")

        rf1 = RuleFile()
        rf1.type = input_entry
        rf1.file = f3

        rf2 = RuleFile()
        rf2.type = output_entry
        rf2.file = f4

        self.__toolwrapper_second = FooWrapper2(rule_name="rule2")
        self.__toolwrapper_second.files.extend([rf1, rf2])

        f5 = IOFilePut(name="output1", path="file4.txt")

        rf1 = RuleFile()
        rf1.type = input_entry
        rf1.file = f3

        rf2 = RuleFile()
        rf2.type = output_entry
        rf2.file = f5

        self.__toolwrapper_third = FooWrapper2(rule_name="rule3")
        self.__toolwrapper_third.files.extend([rf1, rf2])

        f6 = IOFilePut(name="input1", path="file3.txt")
        f7 = IOFilePut(name="input2", path="file4.txt")
        f8 = IOFilePut(name="output1", path="file5.txt")

        rf1 = RuleFile()
        rf1.type = input_entry
        rf1.file = f6

        rf3 = RuleFile()
        rf3.type = input_entry
        rf3.file = f7

        rf2 = RuleFile()
        rf2.type = output_entry
        rf2.file = f8

        self.__toolwrapper_fourth = FooWrapper8(rule_name="rule4")
        self.__toolwrapper_fourth.files.extend([rf1, rf2, rf3])

        list_tool = [self.__toolwrapper_first,
                     self.__toolwrapper_second,
                     self.__toolwrapper_third,
                     self.__toolwrapper_fourth]

        self.__set_tool = set(list_tool)

        SQLManager.instance().get_session().add_all(list_tool)
        SQLManager.instance().get_session().commit()

    def tearDown(self):
        SQLManager.instance().drop_all()

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

