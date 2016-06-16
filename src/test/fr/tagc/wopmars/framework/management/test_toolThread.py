import os
import unittest
from unittest import TestCase

from FooBase import FooBase
from FooWrapper5 import FooWrapper5
from src.main.fr.tagc.wopmars.framework.bdd.SQLManager import SQLManager
from src.main.fr.tagc.wopmars.framework.bdd.tables.IODbPut import IODbPut
from src.main.fr.tagc.wopmars.framework.bdd.tables.IOFilePut import IOFilePut
from src.main.fr.tagc.wopmars.framework.bdd.tables.Option import Option
from src.main.fr.tagc.wopmars.framework.bdd.tables.RuleFile import RuleFile
from src.main.fr.tagc.wopmars.framework.bdd.tables.RuleTable import RuleTable
from src.main.fr.tagc.wopmars.framework.bdd.tables.Type import Type
from src.main.fr.tagc.wopmars.framework.management.ToolThread import ToolThread
from src.main.fr.tagc.wopmars.utils.OptionManager import OptionManager


class TestToolThread(TestCase):

    def setUp(self):
        OptionManager.initial_test_setup()
        SQLManager.instance().create_all()

    def test_run(self):

        input_entry = Type(name="input")
        output_entry = Type(name="output")

        f1 = IOFilePut(name="input1", path="/home/giffon/Documents/wopmars/src/resources/input_File1.txt")
        f2 = IOFilePut(name="output1", path="/home/giffon/Documents/wopmars/src/resources/output_File1.txt")
        t1 = IODbPut(name="FooBase")

        rf1 = RuleFile()
        rf1.file = f1
        rf1.type = input_entry

        rf2 = RuleFile()
        rf2.file = f2
        rf2.type = output_entry

        rt1 = RuleTable()
        rt1.table = t1
        rt1.type = output_entry

        tw1 = FooWrapper5(rule_name="rule1")
        tw1.files.extend([rf1, rf2])
        tw1.tables.append(rt1)

        rf1 = RuleFile()
        rf1.file = f1
        rf1.type = input_entry

        rf2 = RuleFile()
        rf2.file = f2
        rf2.type = output_entry

        rt1 = RuleTable()
        rt1.table = t1
        rt1.type = output_entry

        tw2 = FooWrapper5(rule_name="rule2")
        tw2.files.extend([rf1, rf2])
        tw2.tables.append(rt1)

        rf1 = RuleFile()
        rf1.file = f1
        rf1.type = input_entry

        rf2 = RuleFile()
        rf2.file = f2
        rf2.type = output_entry

        rt1 = RuleTable()
        rt1.table = t1
        rt1.type = output_entry
        tw3 = FooWrapper5(rule_name="rule3")
        tw3.files.extend([rf1, rf2])
        tw3.tables.append(rt1)

        tt1 = ToolThread(tw1)
        tt2 = ToolThread(tw2)
        tt3 = ToolThread(tw3)

        tt1.start()
        tt2.start()
        tt3.start()

        tt1.join()
        tt2.join()
        tt3.join()

        self.assertEqual(len(SQLManager.instance().get_session().query(FooBase).filter(FooBase.name.like('Foowrapper5 - %')).all()), 30)

    def tearDown(self):
        SQLManager.instance().drop_all()
        os.remove("/home/giffon/Documents/wopmars/src/resources/output_File1.txt")

if __name__ == '__main__':
    unittest.main()