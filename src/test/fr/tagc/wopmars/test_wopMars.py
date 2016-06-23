import os
import subprocess
import unittest
from unittest import TestCase

import time

from FooBase2 import FooBase2
from src.main.fr.tagc.wopmars.framework.bdd.SQLManager import SQLManager
from src.main.fr.tagc.wopmars.utils.OptionManager import OptionManager
from src.main.fr.tagc.wopmars.utils.PathFinder import PathFinder
from src.main.fr.tagc.wopmars.wopmars import WopMars


class TestWopMars(TestCase):
    def setUp(self):
        s_root_path = PathFinder.find_src(os.path.dirname(os.path.realpath(__file__)))

        self.__right_def_file = s_root_path + "resources/example_def_file.yml"
        self.__right_def_file_only_files = s_root_path + "resources/example_def_file2.yml"

    def test_run(self):
        cmd_line = ["python", self.__right_def_file, "-vvvv", "-p"]
        with self.assertRaises(SystemExit) as se:
            WopMars().run(cmd_line)
        self.assertEqual(se.exception.code, 0)

    def test_run2(self):
        cmd_line = ["python", self.__right_def_file, "-vvvv", "-p", "--sourcerule", "failure"]
        with self.assertRaises(SystemExit) as se:
            WopMars().run(cmd_line)
        self.assertEqual(se.exception.code, 1)

    def test_run3(self):
        SQLManager.create_all()
        subprocess.Popen(["touch", "/home/giffon/Documents/wopmars/src/resources/outputs/output_File1.txt"])
        subprocess.Popen(["touch", "/home/giffon/Documents/wopmars/src/resources/outputs/output_File4.txt"])
        subprocess.Popen(["touch", "/home/giffon/Documents/wopmars/src/resources/outputs/output_File5.txt"])
        for i in range(10):
            f = FooBase2(name="testwopmars " + str(i))
            SQLManager.instance().get_session().add(f)
        SQLManager.instance().get_session().commit()

        cmd_line = ["python", self.__right_def_file, "-vvvv", "-p", "--sourcerule", "rule6"]
        with self.assertRaises(SystemExit) as se:
            WopMars().run(cmd_line)
        self.assertEqual(se.exception.code, 0)

    def test_run4(self):
        SQLManager.create_all()
        cmd_line = ["python", self.__right_def_file, "-vvvv", "-p", "--targetrule", "rule3"]
        with self.assertRaises(SystemExit) as se:
            WopMars().run(cmd_line)
        self.assertEqual(se.exception.code, 0)

    def test_run5(self):
        cmd_line = ["python", self.__right_def_file_only_files]
        start = time.time()
        with self.assertRaises(SystemExit):
            WopMars().run(cmd_line)
        end = time.time()
        runtime1 = end - start

        start = time.time()
        with self.assertRaises(SystemExit):
            WopMars().run(cmd_line)
        end = time.time()
        runtime2 = end - start

        self.assertGreater(runtime1 * 1.5, runtime2)

        SQLManager.drop_all()
        OptionManager._drop()
        SQLManager._drop()
        PathFinder.silentremove("/home/giffon/Documents/wopmars/src/resources/outputs/output_File1.txt")

        start = time.time()
        with self.assertRaises(SystemExit):
            WopMars().run(cmd_line)
        end = time.time()
        runtime2 = end - start
        self.assertTrue(runtime1 * 0.4 <= runtime2 <= runtime1 * 1.4)

    def test_run5(self):
        cmd_line = ["python", self.__right_def_file, "-p", "-vvvv"]
        start = time.time()
        with self.assertRaises(SystemExit):
            WopMars().run(cmd_line)
        end = time.time()
        runtime1 = end - start
        print(runtime1)

        start = time.time()
        with self.assertRaises(SystemExit):
            WopMars().run(cmd_line)
        end = time.time()
        runtime2 = end - start
        print(runtime2)

        self.assertGreater(runtime1 * 1.5, runtime2)

        SQLManager.drop_all()
        OptionManager._drop()
        SQLManager._drop()
        PathFinder.silentremove("/home/giffon/Documents/wopmars/src/resources/outputs/output_File1.txt")
        print("================================================================================")
        start = time.time()
        with self.assertRaises(SystemExit):
            WopMars().run(cmd_line)
        end = time.time()
        runtime2 = end - start
        print(runtime2)
        self.assertTrue(runtime1 * 0.4 <= runtime2 <= runtime1 * 1.4)

    def get_best_factor(self, full_exec_time, rule_count, maximum_ratio=1):
        average_rule_time = full_exec_time / rule_count
        return 1 + (maximum_ratio * average_rule_time / (1.5 + average_rule_time))

    def tearDown(self):
        SQLManager.drop_all()
        PathFinder.dir_content_remove("/home/giffon/Documents/wopmars/src/resources/outputs/")
        OptionManager._drop()
        SQLManager._drop()

if __name__ == "__main__":
    unittest.main()