from unittest import TestCase

import os
import subprocess
import time
import unittest

from wopmars import OptionManager
from wopmars.framework.database.SQLManager import SQLManager
from wopmars.framework.database.tables.Execution import Execution
from wopmars.utils.PathFinder import PathFinder
from wopmars import WopMars

from wopmars.constants import home_wopmars


class TestWopMars(TestCase):


    def setUp(self):
        if not os.path.isdir(home_wopmars):
            os.makedirs(home_wopmars)
        self.s_root_path = PathFinder.get_module_path()
        os.chdir(self.s_root_path)
        if 'DB_URL' not in os.environ:
            self.__db_url = "sqlite:///" + os.path.join(self.s_root_path, "test/output/db.sqlite")
        else:
            self.__db_url = os.environ['DB_URL']
        #
        self.__example_def_file1 = os.path.join(self.s_root_path, "test/resource/wopfile/example_def_file1.yml")
        self.__example_def_file4 = os.path.join(self.s_root_path, "test/resource/wopfile/example_def_file4.yml")
        self.__example_def_file2_only_files = os.path.join(self.s_root_path, "test/resource/wopfile/example_def_file2_only_files.yml")
        self.__example_def_file5_never_ready = os.path.join(self.s_root_path, "test/resource/wopfile/example_def_file5_never_ready.yml")
        self.__example_def_file_input_not_ready = os.path.join(self.s_root_path, "test/resource/wopfile/example_def_file_input_not_ready.yml")

    def test_01run(self):
        cmd_line = ["python", "-l", "-D", self.__db_url, "-w", self.__example_def_file1, "-v", "-p", "-d", PathFinder.get_module_path()]
        with self.assertRaises(SystemExit) as se:
            WopMars().run(cmd_line)
        self.assertTrue(os.path.exists(os.path.join(self.s_root_path, 'test/output/output_file1.txt')))
        self.assertTrue(os.path.exists(os.path.join(self.s_root_path, 'test/output/output_file2.txt')))
        self.assertTrue(os.path.exists(os.path.join(self.s_root_path, 'test/output/output_file7.txt')))
        self.assertEqual(se.exception.code, 0)

    def test_02dry_run(self):
        cmd_line = ["python", "-n", "-D", self.__db_url, "-w", self.__example_def_file1, "-vv", "-p", "-d",
                    PathFinder.get_module_path()]
        with self.assertRaises(SystemExit) as se:
            WopMars().run(cmd_line)
        self.assertEqual(se.exception.code, 0)

    def test_03run_that_fail(self):
        cmd_line = ["python", "-D", self.__db_url, "-w", self.__example_def_file5_never_ready, "-vv", "-p", "-d",
                    PathFinder.get_module_path()]
        with self.assertRaises(SystemExit) as se:
            WopMars().run(cmd_line)
        self.assertFalse(os.path.exists(os.path.join(self.s_root_path, 'resources/never_done.txt')))
        self.assertEqual(se.exception.code, 1)

    def test_04run_sourcerule_fail(self):
        cmd_line = ["python", "-D", self.__db_url, "-w", self.__example_def_file1, "-vv", "-p", "--sourcerule", "failure"]
        with self.assertRaises(SystemExit) as se:
            WopMars().run(cmd_line)
        self.assertFalse(os.path.exists(os.path.join(self.s_root_path, 'test/output/output_file1.txt')))
        self.assertEqual(se.exception.code, 1)

    def test_05run_sourcerule_succeed(self):
        p=subprocess.Popen(["touch", os.path.join(self.s_root_path, "test/output/output_file1.txt")])
        p.wait()
        p=subprocess.Popen(["touch", os.path.join(self.s_root_path, "test/output/output_file2.txt")])
        p.wait()
        p=subprocess.Popen(["touch", os.path.join(self.s_root_path, "test/output/output_file3.txt")])
        p.wait()
        p=subprocess.Popen(["touch", os.path.join(self.s_root_path, "test/output/output_file4.txt")])
        p.wait()
        cmd_line = ["python", "-D", self.__db_url, "-w", self.__example_def_file1, "-d", PathFinder.get_module_path(), "-vv", "-p", "--sourcerule", "rule2"]
        with self.assertRaises(SystemExit) as se:
            WopMars().run(cmd_line)
        self.assertEqual(se.exception.code, 0)

    def test_06run_skipping_steps_time_check(self):
        cmd_line = ["python", "-D", self.__db_url, "-w", self.__example_def_file2_only_files, "-vv", "-p"]
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
        PathFinder.silentremove("test/output/output_file1.txt")

    def test_07dry_drun_skipping(self):
        cmd_line = ["python", "-D", self.__db_url, "-w", self.__example_def_file2_only_files, "-vv", "-p"]
        with self.assertRaises(SystemExit):
           WopMars().run(cmd_line)

        with self.assertRaises(SystemExit):
           WopMars().run(cmd_line + ["-n"])

    def test_08dry_drun_skipping_all_but_one(self):
        cmd_line = ["python", "-D", self.__db_url, "-w", self.__example_def_file1, "-vv", "-p"]
        with self.assertRaises(SystemExit):
           WopMars().run(cmd_line)
        PathFinder.silentremove("test/output/output_file7.txt")
        with self.assertRaises(SystemExit):
           WopMars().run(cmd_line + ["-n"])

    def test_09run6(self):
        cmd_line = ["python", "-D", self.__db_url, "-w", self.__example_def_file1, "-p", "-vv"]
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
        # SQLManager.instance().drop_all()
        # OptionManager._drop()
        # SQLManager._drop()
        # PathFinder.silentremove("test/output/output_file1.txt")
        # start = time.time()
        # with self.assertRaises(SystemExit):
        #    WopMars().run(cmd_line)
        # end = time.time()
        # runtime2 = end - start
        # self.assertTrue(runtime1 * 0.4 <= runtime2 <= runtime1 * 1.4)

    def get_best_factor(self, full_exec_time, rule_count, maximum_ratio=1):
        average_rule_time = full_exec_time / rule_count
        return 1 + (maximum_ratio * average_rule_time / (1.5 + average_rule_time))

    def test_10run_error_in_command_line(self):
        cmd_line = ["python", "-D", self.__db_url, "-w", self.__example_def_file1, "--dot", "/usr/"]
        with self.assertRaises(SystemExit) as SE:
            WopMars().run(cmd_line)
        self.assertEqual(SE.exception.code, 2)

        cmd_line = ["python", "-D", self.__db_url, "-w", self.__example_def_file1, "--not-known"]
        with self.assertRaises(SystemExit) as SE:
            WopMars().run(cmd_line)
        self.assertEqual(SE.exception.code, 2)

    def test_run_packaged_wrappers(self):
        cmd_line = ["python", "-D", self.__db_url, "-w", self.__example_def_file4, "-vv", "-p", "-d",
                    PathFinder.get_module_path()]
        with self.assertRaises(SystemExit) as se:
            WopMars().run(cmd_line)
        self.assertEqual(se.exception.code, 0)

    def test_run_one_tool(self):
        cmd_line = ["python", "tool", "test.resource.wrapper.FooWrapper4",
                  "-i", "{'file': {'input1': 'test/resource/input_files/input_file1.txt'}}",
                  "-o", "{'file': {'output1': 'test/output/output1.txt'}}", "-D", self.__db_url, "-vv", "-p", "-d",
                  PathFinder.get_module_path()]
        with self.assertRaises(SystemExit) as se:
            WopMars().run(cmd_line)
        self.assertEqual(se.exception.code, 0)

    def test_core(self):
        cmd_line = ["python", "tool", "test.resource.wrapper.FooWrapperCore",
                  "-o", "{'table': {'FooBase7': 'test.resource.model.FooBase7'}}",
                  "-vv", "-p", "-D", self.__db_url, "-d", PathFinder.get_module_path()]
        with self.assertRaises(SystemExit) as se:
           WopMars().run(cmd_line)
        self.assertEqual(se.exception.code, 0)

    def test_clear_history(self):
        cmd_line = ["python", "-D", self.__db_url,
                  "-w", self.__example_def_file1,
                  "-vv", "-p", "-d", PathFinder.get_module_path(), "-c", "-F"]
        with self.assertRaises(SystemExit):
               WopMars().run(cmd_line)
               WopMars().run(cmd_line)
        session = SQLManager.instance().get_session()
        self.assertEqual(session.query(Execution).count(), 1)

    # def test_pandas(self):
    #     cmd_line = ["python", "tool", "test.resource.wrapper.FooWrapperDataframe",
    #                 "-o", "{'table': {'FooBase': 'test.resource.model.FooBase'}}",
    #                 "-vv", "-p", "-D", self.__db_url, "-d", PathFinder.get_module_path()]
    #
    #     with self.assertRaises(SystemExit) as se:
    #         WopMars().run(cmd_line)
    #
    #     self.assertEqual(se.exception.code, 1)

    def test_run_target_rule(self):
        # SQLManager.instance().create_all()
        cmd_line = ["python", "-D", self.__db_url, "-w", self.__example_def_file1, "-vv", "-p", "--targetrule", "rule3"]
        with self.assertRaises(SystemExit) as se:
           WopMars().run(cmd_line)
        self.assertEqual(se.exception.code, 0)

    def test_run_input_file_not_ready(self):
        # SQLManager.instance().create_all()
        cmd_line = ["python", "-D", self.__db_url, "-w", self.__example_def_file_input_not_ready, "-vv", "-p"]
        with self.assertRaises(SystemExit) as se:
           WopMars().run(cmd_line)
        self.assertEqual(se.exception.code, 1)

    def tearDown(self):
        SQLManager.instance().get_session().close()
        SQLManager.instance().drop_all()
        PathFinder.dir_content_remove(os.path.join(self.s_root_path, "test/output"))
        OptionManager._drop()
        SQLManager._drop()

if __name__ == "__main__":
    unittest.main()


