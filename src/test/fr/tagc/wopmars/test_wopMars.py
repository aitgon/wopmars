import os
import subprocess
import unittest
from unittest import TestCase

from FooBase2 import FooBase2
from src.main.fr.tagc.wopmars.framework.bdd.SQLManager import SQLManager
from src.main.fr.tagc.wopmars.utils.OptionManager import OptionManager
from src.main.fr.tagc.wopmars.utils.PathFinder import PathFinder
from src.main.fr.tagc.wopmars.wopmars import WopMars


class TestWopMars(TestCase):
    def setUp(self):
        s_root_path = PathFinder.find_src(os.path.dirname(os.path.realpath(__file__)))

        self.__right_def_file = s_root_path + "resources/example_def_file.yml"

    def test_run(self):
        cmd_line = [self.__right_def_file, "-vvvv", "-n"]
        with self.assertRaises(SystemExit) as se:
            WopMars().run(cmd_line)
        self.assertEqual(se.exception.code, 0)

    def test_run2(self):
        cmd_line = [self.__right_def_file, "-vvvv", "-n", "--from", "failure"]
        with self.assertRaises(SystemExit) as se:
            WopMars().run(cmd_line)
        self.assertEqual(se.exception.code, 1)

    def test_run3(self):
        SQLManager.instance().create_all()
        subprocess.Popen(["touch", "/home/giffon/Documents/wopmars/src/resources/output_File1.txt"])
        subprocess.Popen(["touch", "/home/giffon/Documents/wopmars/src/resources/output_File4.txt"])
        subprocess.Popen(["touch", "/home/giffon/Documents/wopmars/src/resources/output_File5.txt"])
        for i in range(10):
            f = FooBase2(name="testwopmars " + str(i))
            SQLManager.instance().get_session().add(f)
        SQLManager.instance().get_session().commit()

        cmd_line = [self.__right_def_file, "-vvvv", "-n", "--from", "rule6"]
        with self.assertRaises(SystemExit) as se:
            WopMars().run(cmd_line)
        self.assertEqual(se.exception.code, 0)

    def test_run4(self):
        SQLManager.instance().create_all()
        cmd_line = [self.__right_def_file, "-vvvv", "-n", "--to", "rule3"]
        with self.assertRaises(SystemExit) as se:
            WopMars().run(cmd_line)
        self.assertEqual(se.exception.code, 0)

    def tearDown(self):
        SQLManager.instance().drop_all()
        PathFinder.silentremove("/home/giffon/Documents/wopmars/src/resources/output_File1.txt")
        PathFinder.silentremove("/home/giffon/Documents/wopmars/src/resources/output_File2.txt")
        PathFinder.silentremove("/home/giffon/Documents/wopmars/src/resources/output_File3.txt")
        PathFinder.silentremove("/home/giffon/Documents/wopmars/src/resources/output_File4.txt")
        PathFinder.silentremove("/home/giffon/Documents/wopmars/src/resources/output_File5.txt")
        PathFinder.silentremove("/home/giffon/Documents/wopmars/src/resources/output_File6.txt")
        PathFinder.silentremove("/home/giffon/Documents/wopmars/src/resources/output_File7.txt")
        OptionManager._drop()
        SQLManager._drop()

if __name__ == "__main__":
    unittest.main()