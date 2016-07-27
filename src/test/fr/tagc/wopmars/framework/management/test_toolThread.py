import os
import threading
import unittest
from unittest import TestCase

import time

import datetime

import sprintFive
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
from src.main.fr.tagc.wopmars.utils.PathFinder import PathFinder
from sprintFive.Add import Add as tw_add
from sprintFive.Query import Query as tw_query


class TestToolThread(TestCase):

    def setUp(self):
        OptionManager.initial_test_setup()
        SQLManager.instance().create_all()

        [SQLManager.instance().get_session().add(FooBase(name="foo " + str(i))) for i in range(10000)]
        SQLManager.instance().get_session().commit()

    def test_run(self):

        input_entry = Type(name="input")
        output_entry = Type(name="output")

        f1 = IOFilePut(name="input1", path="resources/input_File1.txt")
        f1.type = input_entry

        f2 = IOFilePut(name="output1", path="resources/outputs/output_File1.txt")
        f2.type = output_entry

        t1 = IODbPut(name="FooBase")
        t1.set_table(FooBase)
        t1.type = output_entry
        modification_table_entry = ModificationTable(date=datetime.datetime.fromtimestamp(time.time()), table_name=t1.name)
        t1.modification = modification_table_entry

        tw1 = FooWrapper5(rule_name="rule1")
        tw1.files.extend([f1, f2])
        tw1.tables.append(t1)

        f12 = IOFilePut(name="input1", path="resources/input_File1.txt")
        f12.type = input_entry

        f22 = IOFilePut(name="output1", path="resources/outputs/output_File1.txt")
        f22.type = output_entry

        t12 = IODbPut(name="FooBase")
        t12.set_table(FooBase)
        t12.type = output_entry
        modification_table_entry = ModificationTable(
            date=datetime.datetime.fromtimestamp(time.time()), table_name=t12.name)
        t12.modification = modification_table_entry

        tw2 = FooWrapper5(rule_name="rule2")
        tw2.files.extend([f12, f22])
        tw2.tables.append(t12)

        f13 = IOFilePut(name="input1", path="resources/input_File1.txt")
        f13.type = input_entry

        f23 = IOFilePut(name="output1", path="resources/outputs/output_File1.txt")
        f23.type = output_entry

        t13 = IODbPut(name="FooBase")
        t13.set_table(FooBase)
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

        self.assertEqual(len(SQLManager.instance().get_session().query(FooBase).filter(FooBase.name.like('Foowrapper5 - %')).all()), 3000)

    def test_run_commit_vs_query(self):
        input_entry = Type(name="input")
        output_entry = Type(name="output")

        f1 = IOFilePut(name="input1", path="resources/input_File1.txt")
        f1.type = input_entry

        t1 = IODbPut(name="FooBase")
        t1.set_table(FooBase)
        t1.type = output_entry
        modification_table_entry = ModificationTable(date=datetime.datetime.fromtimestamp(time.time()), table_name=t1.name)
        t1.modification = modification_table_entry

        o1 = Option(name="rows", value="1000")

        tw1 = tw_add(rule_name="rule1")
        tw1.files.append(f1)
        tw1.tables.append(t1)
        tw1.options.append(o1)

        f12 = IOFilePut(name="input1", path="resources/input_File1.txt")
        f12.type = input_entry

        t12 = IODbPut(name="FooBase")
        t12.set_table(FooBase)
        t12.type = output_entry
        modification_table_entry = ModificationTable(date=datetime.datetime.fromtimestamp(time.time()),
                                                     table_name=t12.name)
        t12.modification = modification_table_entry

        o12 = Option(name="rows", value="1000")

        tw12 = tw_add(rule_name="rule1")
        tw12.files.append(f12)
        tw12.tables.append(t12)
        tw12.options.append(o12)

        f13 = IOFilePut(name="input1", path="resources/input_File1.txt")
        f13.type = input_entry

        t13 = IODbPut(name="FooBase")
        t13.set_table(FooBase)
        t13.type = output_entry
        modification_table_entry = ModificationTable(date=datetime.datetime.fromtimestamp(time.time()),
                                                     table_name=t13.name)
        t13.modification = modification_table_entry

        o13 = Option(name="rows", value="1000")

        tw13 = tw_add(rule_name="rule1")
        tw13.files.append(f13)
        tw13.tables.append(t13)
        tw13.options.append(o13)

        tt1 = ToolThread(tw1)
        tt2 = ToolThread(tw12)
        tt3 = ToolThread(tw13)

        t21 = IODbPut(name="FooBase")
        t21.set_table(FooBase)
        t21.type = input_entry

        tw21 = tw_query(rule_name="rule1")
        tw21.tables.append(t21)

        t22 = IODbPut(name="FooBase")
        t22.set_table(FooBase)
        t22.type = input_entry

        tw22 = tw_query(rule_name="rule1")
        tw22.tables.append(t22)

        t23 = IODbPut(name="FooBase")
        t23.set_table(FooBase)
        t23.type = input_entry

        tw23 = tw_query(rule_name="rule1")
        tw23.tables.append(t23)

        tt4 = ToolThread(tw21)
        tt5 = ToolThread(tw22)
        tt6 = ToolThread(tw23)

        tt4.start()

        tt1.start()
        tt2.start()
        tt3.start()
        time.sleep(5)
        tt5.start()
        tt6.start()

        tt1.join()
        tt2.join()
        tt3.join()
        tt4.join()
        tt5.join()
        tt6.join()

    def tearDown(self):
        SQLManager.instance().drop_all()
        PathFinder.silentremove("resources/outputs/")

if __name__ == '__main__':
    unittest.main()