import os
import subprocess
import unittest
from unittest import TestCase

import time

from FooBase2 import FooBase2
from wopmars.main.tagc.framework.bdd.SQLManager import SQLManager
from wopmars.main.tagc.framework.bdd.tables.Execution import Execution
from wopmars.main.tagc.utils.OptionManager import OptionManager
from wopmars.main.tagc.utils.PathFinder import PathFinder
from wopmars import WopMars


class TestWopMars(TestCase):
    def setUp(self):
        print(os.path.dirname(os.path.realpath(__file__)))
        s_root_path = PathFinder.find_src(os.path.dirname(os.path.realpath(__file__)))
        print(s_root_path)
        os.chdir(s_root_path)
        self.__db_path = s_root_path + "resources/outputs/db.sqlite"
        self.__right_def_file = s_root_path + "resources/example_def_file.yml"
        self.__right_def_file2 = s_root_path + "resources/example_def_file4.yml"
        self.__right_def_file_only_files = s_root_path + "resources/example_def_file2.yml"
        self.__def_file_never_ready = s_root_path + "resources/example_def_file_toolwrapper_never_ready.yml"

    def test_run(self):
        cmd_line = ["python", "-l", "-D", self.__db_path, "-w", self.__right_def_file, "-v", "-p", "-d", PathFinder.find_src(os.path.realpath(__file__))]
        with self.assertRaises(SystemExit) as se:
            WopMars().run(cmd_line)
        self.assertEqual(se.exception.code, 0)

    def test_dry_run(self):
        cmd_line = ["python", "-n", "-D", self.__db_path, "-w", self.__right_def_file, "-vv", "-p", "-d",
                    PathFinder.find_src(os.path.realpath(__file__))]

        with self.assertRaises(SystemExit) as se:
            WopMars().run(cmd_line)
        self.assertEqual(se.exception.code, 0)

    def test_run_that_fail(self):
        cmd_line = ["python", "-D", self.__db_path, "-w", self.__def_file_never_ready, "-vv", "-p", "-d",
                    PathFinder.find_src(os.path.realpath(__file__))]
        with self.assertRaises(SystemExit) as se:
            WopMars().run(cmd_line)
        self.assertEqual(se.exception.code, 1)

    def test_run_sourcerule_fail(self):
        cmd_line = ["python", "-D", self.__db_path, "-w", self.__right_def_file, "-vv", "-p", "--sourcerule", "failure"]
        with self.assertRaises(SystemExit) as se:
            WopMars().run(cmd_line)
        self.assertEqual(se.exception.code, 1)

    def test_run_sourcerule_succeed(self):
        SQLManager.instance().create_all()
        subprocess.Popen(["touch", "resources/outputs/output_File1.txt"])
        subprocess.Popen(["touch", "resources/outputs/output_File4.txt"])
        subprocess.Popen(["touch", "resources/outputs/output_File5.txt"])
        for i in range(10):
            f = FooBase2(name="testwopmars " + str(i))
            SQLManager.instance().get_session().add(f)
        SQLManager.instance().get_session().commit()

        cmd_line = ["python", "-D", self.__db_path, "-w", self.__right_def_file, "-vv", "-p", "--sourcerule", "rule6"]
        with self.assertRaises(SystemExit) as se:
            WopMars().run(cmd_line)
        self.assertEqual(se.exception.code, 0)

    def test_run_target_rule(self):
        SQLManager.instance().create_all()
        cmd_line = ["python", "-D", self.__db_path, "-w", self.__right_def_file, "-vv", "-p", "--targetrule", "rule3"]
        with self.assertRaises(SystemExit) as se:
            WopMars().run(cmd_line)
        self.assertEqual(se.exception.code, 0)

    def test_run_skiping_steps_time_check(self):
        cmd_line = ["python", "-D", self.__db_path, "-w", self.__right_def_file_only_files, "-vv", "-p"]
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

        SQLManager.instance().drop_all()
        OptionManager._drop()
        SQLManager._drop()
        PathFinder.silentremove("resources/outputs/output_File1.txt")

        start = time.time()
        with self.assertRaises(SystemExit):
            WopMars().run(cmd_line)
        end = time.time()
        runtime2 = end - start
        self.assertTrue(runtime1 * 0.4 <= runtime2 <= runtime1 * 1.4)

    def test_dry_drun_skipping(self):
        cmd_line = ["python", "-D", self.__db_path, "-w", self.__right_def_file_only_files, "-vv", "-p"]
        with self.assertRaises(SystemExit):
            WopMars().run(cmd_line)

        with self.assertRaises(SystemExit):
            WopMars().run(cmd_line + ["-n"])

    def test_dry_drun_skipping_all_but_one(self):
        cmd_line = ["python", "-D", self.__db_path, "-w", self.__right_def_file, "-vv", "-p"]
        with self.assertRaises(SystemExit):
            WopMars().run(cmd_line)

        PathFinder.silentremove("resources/outputs/output_File7.txt")

        with self.assertRaises(SystemExit):
            WopMars().run(cmd_line + ["-n"])

    def test_run6(self):
        cmd_line = ["python", "-D", self.__db_path, "-w", self.__right_def_file, "-p", "-vv"]
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

        SQLManager.instance().drop_all()
        OptionManager._drop()
        SQLManager._drop()
        PathFinder.silentremove("resources/outputs/output_File1.txt")
        start = time.time()
        with self.assertRaises(SystemExit):
            WopMars().run(cmd_line)
        end = time.time()
        runtime2 = end - start
        self.assertTrue(runtime1 * 0.4 <= runtime2 <= runtime1 * 1.4)

    def get_best_factor(self, full_exec_time, rule_count, maximum_ratio=1):
        average_rule_time = full_exec_time / rule_count
        return 1 + (maximum_ratio * average_rule_time / (1.5 + average_rule_time))

    def test_run_error_in_command_line(self):
        cmd_line = ["python", "-D", self.__db_path, "-w", self.__right_def_file, "--dot", "/usr/"]
        with self.assertRaises(SystemExit) as SE:
            WopMars().run(cmd_line)
        self.assertEqual(SE.exception.code, 2)

        cmd_line = ["python", "-D", self.__db_path, "-w", self.__right_def_file, "--not-known"]
        with self.assertRaises(SystemExit) as SE:
            WopMars().run(cmd_line)
        self.assertEqual(SE.exception.code, 2)

    def test_run_packaged_wrappers(self):
        cmd_line = ["python", "-D", self.__db_path, "-w", self.__right_def_file2, "-vv", "-p", "-d",
                    PathFinder.find_src(os.path.realpath(__file__))]
        with self.assertRaises(SystemExit) as se:
            WopMars().run(cmd_line)
        self.assertEqual(se.exception.code, 0)

    def test_run_one_tool(self):
        cmd_line = ["python", "tool", "FooWrapper4",
                    "-i", "{'file': {'input1': 'resources/input_File1.txt'}}",
                    "-o", "{'file': {'output1': 'resources/outputs/output1.txt'}}", "-D", self.__db_path, "-vv", "-p", "-d",
                    PathFinder.find_src(os.path.realpath(__file__))]
        with self.assertRaises(SystemExit) as se:
            WopMars().run(cmd_line)
        self.assertEqual(se.exception.code, 0)

    def test_core(self):
        cmd_line = ["python", "tool", "FooWrapperCore",
                    "-o", "{'table': {'FooBase': 'FooBase'}}",
                    "-vv", "-p", "-D", self.__db_path, "-d", PathFinder.find_src(os.path.realpath(__file__))]
        with self.assertRaises(SystemExit) as se:
            WopMars().run(cmd_line)
        self.assertEqual(se.exception.code, 0)

    def test_clear_history(self):
        cmd_line = ["python", "-D", self.__db_path,
                    "-w", self.__right_def_file,
                    "-vv", "-p", "-d", PathFinder.find_src(os.path.realpath(__file__)), "-c", "-F"]
        with self.assertRaises(SystemExit):
            WopMars().run(cmd_line)
            WopMars().run(cmd_line)
        session = SQLManager.instance().get_session()
        self.assertEqual(session.query(Execution).count(), 1)

    def test_pandas(self):
        cmd_line = ["python", "tool", "FooWrapperDataframe",
                    "-o", "{'table': {'FooBase': 'FooBase'}}",
                    "-vv", "-p", "-D", self.__db_path, "-d", PathFinder.find_src(os.path.realpath(__file__))]

        with self.assertRaises(SystemExit) as se:
            WopMars().run(cmd_line)

        self.assertEqual(se.exception.code, 0)

    def tearDown(self):
        SQLManager.instance().drop_all()
        PathFinder.dir_content_remove("resources/outputs/")
        # OptionManager._drop()
        SQLManager._drop()

if __name__ == "__main__":
    unittest.main()