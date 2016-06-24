import os
import unittest
from unittest import TestCase

import time

import datetime

from FooBase import FooBase
from FooWrapper5 import FooWrapper5
from src.main.fr.tagc.wopmars.framework.bdd.SQLManager import SQLManager
from src.main.fr.tagc.wopmars.framework.bdd.tables.IODbPut import IODbPut
from src.main.fr.tagc.wopmars.framework.bdd.tables.IOFilePut import IOFilePut
from src.main.fr.tagc.wopmars.framework.bdd.tables.ModificationTable import ModificationTable
from src.main.fr.tagc.wopmars.framework.bdd.tables.Option import Option
from src.main.fr.tagc.wopmars.framework.bdd.tables.Type import Type
from src.main.fr.tagc.wopmars.framework.management.ToolThread import ToolThread
from src.main.fr.tagc.wopmars.utils.OptionManager import OptionManager


class TestToolThread(TestCase):

    def setUp(self):
        OptionManager.initial_test_setup()
        SQLManager.create_all()

    def test_run(self):

        input_entry = Type(name="input")
        output_entry = Type(name="output")

        f1 = IOFilePut(name="input1", path="/home/giffon/Documents/wopmars/src/resources/input_File1.txt")
        f1.type = input_entry

        f2 = IOFilePut(name="output1", path="/home/giffon/Documents/wopmars/src/resources/outputs/output_File1.txt")
        f2.type = output_entry

        t1 = IODbPut(name="FooBase")
        t1.type = output_entry
        modification_table_entry = ModificationTable(date=datetime.datetime.fromtimestamp(time.time()), table_name=t1.name)
        t1.modification = modification_table_entry

        tw1 = FooWrapper5(rule_name="rule1")
        tw1.files.extend([f1, f2])
        tw1.tables.append(t1)

        f12 = IOFilePut(name="input1", path="/home/giffon/Documents/wopmars/src/resources/input_File1.txt")
        f12.type = input_entry

        f22 = IOFilePut(name="output1", path="/home/giffon/Documents/wopmars/src/resources/outputs/output_File1.txt")
        f22.type = output_entry

        t12 = IODbPut(name="FooBase")
        t12.type = output_entry
        modification_table_entry = ModificationTable(
            date=datetime.datetime.fromtimestamp(time.time()), table_name=t12.name)
        t12.modification = modification_table_entry

        tw2 = FooWrapper5(rule_name="rule2")
        tw2.files.extend([f12, f22])
        tw2.tables.append(t12)

        f13 = IOFilePut(name="input1", path="/home/giffon/Documents/wopmars/src/resources/input_File1.txt")
        f13.type = input_entry

        f23 = IOFilePut(name="output1", path="/home/giffon/Documents/wopmars/src/resources/outputs/output_File1.txt")
        f23.type = output_entry

        t13 = IODbPut(name="FooBase")
        t13.type = output_entry
        modification_table_entry = ModificationTable(
            date=datetime.datetime.fromtimestamp(time.time()), table_name=t13.name)
        t13.modification = modification_table_entry

        tw3 = FooWrapper5(rule_name="rule3")
        tw3.files.extend([f13, f23])
        tw3.tables.append(t13)

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
        SQLManager.drop_all()
        os.remove("/home/giffon/Documents/wopmars/src/resources/outputs/output_File1.txt")

if __name__ == '__main__':
    unittest.main()