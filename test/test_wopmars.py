import pathlib
from unittest import TestCase

import os
import subprocess
import unittest

from wopmars import OptionManager
from wopmars.SQLManager import SQLManager
from wopmars.models.Execution import Execution
from wopmars.utils.PathFinder import PathFinder
from wopmars import WopMars

from wopmars.utils.various import get_current_time
from wopmars.Base import Base


class TestWopmars(TestCase):


    def setUp(self):
        self.s_root_path = PathFinder.get_module_path()
        os.chdir(self.s_root_path)
        #
        # Intial test options
        #
        OptionManager.initial_test_setup()
        self.__db_url = OptionManager.instance()["--database"]
        if 'DB_URL' in os.environ:
            self.__db_url = os.environ['DB_URL']
        #
        self.__example_def_file1 = os.path.join(self.s_root_path, "test/resource/wopfile/example_def_file1.yml")
        self.__example_def_file1_only_database = \
            os.path.join(self.s_root_path, "test/resource/wopfile/example_def_file1_only_database.yml")
        self.__example_def_file2_only_files = os.path.join(self.s_root_path, "test/resource/wopfile/example_def_file2_only_files.yml")
        self.__example_def_file4 = os.path.join(self.s_root_path, "test/resource/wopfile/example_def_file4.yml")
        self.__example_def_file5_never_ready = os.path.join(self.s_root_path, "test/resource/wopfile/example_def_file5_never_ready.yml")
        self.__example_def_file_input_not_ready = os.path.join(self.s_root_path, "test/resource/wopfile/example_def_file_input_not_ready.yml")

    def tearDown(self):
        SQLManager.instance().get_session().close()
        SQLManager.instance().drop_all()
        PathFinder.dir_content_remove(os.path.join(self.s_root_path, "test/output"))
        OptionManager._drop()
        SQLManager._drop()

    def test_01run(self):
        cmd_line = ["python", "-D", self.__db_url, "-w", self.__example_def_file1, "-vv", "-d", PathFinder.get_module_path()]
        with self.assertRaises(SystemExit) as se:
            WopMars().run(cmd_line)
        self.assertTrue(os.path.exists(os.path.join(self.s_root_path, 'test/output/output_file1.txt')))
        self.assertTrue(os.path.exists(os.path.join(self.s_root_path, 'test/output/output_file2.txt')))
        self.assertTrue(os.path.exists(os.path.join(self.s_root_path, 'test/output/output_file7.txt')))
        self.assertEqual(se.exception.code, 0)

    def test_db_forceall(self):
        """Tests the forceall option in the database. Will carry out different runs in either default or forceall mode
        that will either increase or keep same the number of rows of the FooBase table"""

        pathlib.Path(os.path.join(self.s_root_path, "test/output/output_file1.txt")).touch()

        ################################################################################################################
        #
        # Run 1: normal mode. Results in 1000 rows
        #
        ################################################################################################################

        cmd_line = ["python", "-D", self.__db_url, "-w", self.__example_def_file1_only_database, "-vv",
                    "-d", PathFinder.get_module_path()]
        with self.assertRaises(SystemExit) as se:
            WopMars().run(cmd_line)
        foobase_model = Base.metadata.tables['FooBase']
        row_count = SQLManager.instance().get_session().query(foobase_model).count()
        self.assertTrue(row_count == 1000)
        self.assertEqual(se.exception.code, 0)

        ################################################################################################################
        #
        # Run 2: normal mode. Still 1000 rows, because it does not execute
        #
        ################################################################################################################

        cmd_line = ["python", "-D", self.__db_url, "-w", self.__example_def_file1_only_database, "-vv",
                    "-d", PathFinder.get_module_path()]
        with self.assertRaises(SystemExit) as se:
            WopMars().run(cmd_line)
        row_count = SQLManager.instance().get_session().query(foobase_model).count()
        self.assertTrue(row_count == 1000)
        self.assertEqual(se.exception.code, 0)

        ################################################################################################################
        #
        # Run 3: forceall mode. Now 2000 rows, because it is forced to execute
        #
        ################################################################################################################

        cmd_line = ["python", "-D", self.__db_url, "-w", self.__example_def_file1_only_database, "-vv",
                    "-d", PathFinder.get_module_path(), "--forceall"]
        with self.assertRaises(SystemExit) as se:
            WopMars().run(cmd_line)
        row_count = SQLManager.instance().get_session().query(foobase_model).count()
        self.assertTrue(row_count == 2000)
        self.assertEqual(se.exception.code, 0)

        ################################################################################################################
        #
        # Run 4: normal mode. Again 2000 rows, because it does not execute
        #
        ################################################################################################################

        cmd_line = ["python", "-D", self.__db_url, "-w", self.__example_def_file1_only_database, "-vv",
                    "-d", PathFinder.get_module_path()]
        with self.assertRaises(SystemExit) as se:
            WopMars().run(cmd_line)
        row_count = SQLManager.instance().get_session().query(foobase_model).count()
        self.assertTrue(row_count == 2000)
        self.assertEqual(se.exception.code, 0)

    def test_forceall_dryrun(self):
        """This test carries out a normal a forceall and a dryrun and stores the modification times.
        Then it will test that the modification time of the two first outputs are different and the
         second and third equal"""
        cmd_line = ["python", "-D", self.__db_url, "-w", self.__example_def_file1, "-vv", "-d", PathFinder.get_module_path()]
        with self.assertRaises(SystemExit) as se:
            WopMars().run(cmd_line)
        # Test that modification date of first run is different from second forced run
        mtime1 = os.path.getmtime(os.path.join(self.s_root_path, 'test/output/output_file7.txt'))
        # Run forceall
        cmd_line_force = ["python", "-D", self.__db_url, "-w", self.__example_def_file1, "-vv",
                    "-d", PathFinder.get_module_path(), "--forceall"]
        with self.assertRaises(SystemExit) as se:
            WopMars().run(cmd_line_force)
        mtime2 = os.path.getmtime(os.path.join(self.s_root_path, 'test/output/output_file7.txt'))
        # Run dry-run
        cmd_line_dry_run = ["python", "-D", self.__db_url, "-w", self.__example_def_file1, "-vv",
                    "-d", PathFinder.get_module_path(), "--dry-run"]
        with self.assertRaises(SystemExit) as se:
            WopMars().run(cmd_line_dry_run)
        mtime3 = os.path.getmtime(os.path.join(self.s_root_path, 'test/output/output_file7.txt'))
        # Assert first two modification times are different
        # Assert second and third modification times same
        self.assertTrue(mtime1 != mtime2)
        self.assertTrue(mtime2 == mtime3)
        self.assertEqual(se.exception.code, 0)

    def test_dry_run(self):
        cmd_line = ["python", "--dry-run", "-D", self.__db_url, "-w", self.__example_def_file1, "-vv", "-d",
                    PathFinder.get_module_path()]
        with self.assertRaises(SystemExit) as se:
            WopMars().run(cmd_line)
        # The test is that these files do not exist
        self.assertFalse(os.path.exists(os.path.join(self.s_root_path, 'test/output/output_file1.txt')))
        self.assertFalse(os.path.exists(os.path.join(self.s_root_path, 'test/output/output_file2.txt')))
        self.assertFalse(os.path.exists(os.path.join(self.s_root_path, 'test/output/output_file7.txt')))
        self.assertEqual(se.exception.code, 0)

    def test_03run_that_fail(self):
        cmd_line = ["python", "-D", self.__db_url, "-w", self.__example_def_file5_never_ready, "-vv", "-d",
                    PathFinder.get_module_path()]
        with self.assertRaises(SystemExit) as se:
            WopMars().run(cmd_line)
        self.assertFalse(os.path.exists(os.path.join(self.s_root_path, 'resources/never_done.txt')))
        self.assertEqual(se.exception.code, 1)

    def test_04run_sourcerule_fail(self):
        cmd_line = ["python", "-D", self.__db_url, "-w", self.__example_def_file1, "-vv", "--since", "failure"]
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
        cmd_line = ["python", "-D", self.__db_url, "-w", self.__example_def_file1, "-d", PathFinder.get_module_path(), "-vv", "--since", "rule2"]
        with self.assertRaises(SystemExit) as se:
            WopMars().run(cmd_line)
        self.assertEqual(se.exception.code, 0)

    def test_06run_skipping_steps_time_check(self):
        cmd_line = ["python", "-D", self.__db_url, "-w", self.__example_def_file2_only_files, "-vv"]
        time_unix_ms, time_human = get_current_time()
        start = time_unix_ms
        with self.assertRaises(SystemExit):
           WopMars().run(cmd_line)
        time_unix_ms, time_human = get_current_time()
        end = time_unix_ms
        runtime1 = end - start
        time_unix_ms, time_human = get_current_time()
        start = time_unix_ms
        with self.assertRaises(SystemExit):
           WopMars().run(cmd_line)
        time_unix_ms, time_human = get_current_time()
        end = time_unix_ms
        runtime2 = end - start
        self.assertGreater(runtime1 * 1.5, runtime2)
        PathFinder.silentremove("test/output/output_file1.txt")

    def test_07dry_drun_skipping(self):
        cmd_line = ["python", "-D", self.__db_url, "-w", self.__example_def_file2_only_files, "-vv"]
        with self.assertRaises(SystemExit):
           WopMars().run(cmd_line)

        with self.assertRaises(SystemExit):
           WopMars().run(cmd_line + ["-n"])

    def test_08dry_drun_skipping_all_but_one(self):
        cmd_line = ["python", "-D", self.__db_url, "-w", self.__example_def_file1, "-vv"]
        with self.assertRaises(SystemExit):
           WopMars().run(cmd_line)
        PathFinder.silentremove("test/output/output_file7.txt")
        with self.assertRaises(SystemExit):
           WopMars().run(cmd_line + ["-n"])

    def test_09run6(self):
        cmd_line = ["python", "-D", self.__db_url, "-w", self.__example_def_file1, "-vv"]
        time_unix_ms, time_human = get_current_time()
        start = time_unix_ms
        with self.assertRaises(SystemExit):
            WopMars().run(cmd_line)
        time_unix_ms, time_human = get_current_time()
        end = time_unix_ms
        runtime1 = end - start
        time_unix_ms, time_human = get_current_time()
        start = time_unix_ms
        with self.assertRaises(SystemExit):
            WopMars().run(cmd_line)
        time_unix_ms, time_human = get_current_time()
        end = time_unix_ms
        runtime2 = end - start
        self.assertGreater(runtime1 * 1.5, runtime2)
        PathFinder.silentremove("test/output/output_file1.txt")
        time_unix_ms, time_human = get_current_time()
        start = time_unix_ms
        with self.assertRaises(SystemExit):
            WopMars().run(cmd_line)
        time_unix_ms, time_human = get_current_time()
        end = time_unix_ms
        runtime2 = end - start
        self.assertTrue(runtime1 * 0.4 <= runtime2 <= runtime1 * 1.4)

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
        cmd_line = ["python", "-D", self.__db_url, "-w", self.__example_def_file4, "-vv", "-d",
                    PathFinder.get_module_path()]
        with self.assertRaises(SystemExit) as se:
            WopMars().run(cmd_line)
        self.assertEqual(se.exception.code, 0)

    def test_run_one_tool(self):
        cmd_line = ["python", "tool", "test.resource.wrapper.FooWrapper4",
                  "-i", "{'file': {'input1': 'test/resource/input_files/input_file1.txt'}}",
                  "-o", "{'file': {'output1': 'test/output/output1.txt'}}", "-D", self.__db_url, "-vv", "-d",
                  PathFinder.get_module_path()]
        with self.assertRaises(SystemExit) as se:
            WopMars().run(cmd_line)
        self.assertEqual(se.exception.code, 0)

    # AG Do not know why but it is not working
    # def test_core(self):
    #     cmd_line = ["python", "tool", "test.resource.wrapper.FooWrapperCore",
    #               "-o", "{'table': {'FooBase7': 'test.resource.model.FooBase7'}}",
    #               "-vv", "-D", self.__db_url, "-d", PathFinder.get_module_path()]
    #     with self.assertRaises(SystemExit) as se:
    #        WopMars().run(cmd_line)
    #     self.assertEqual(se.exception.code, 0)

    def test_clear_history(self):
        cmd_line = ["python", "-D", self.__db_url, "-w", self.__example_def_file1, "-vv",
                    "-d", PathFinder.get_module_path()]
        cmd_line_clear_history = ["python", "-D", self.__db_url, "-w", self.__example_def_file1, "-vv",
                    "-d", PathFinder.get_module_path(), "--clear-history"]
        with self.assertRaises(SystemExit):
            WopMars().run(cmd_line)
        with self.assertRaises(SystemExit):
            WopMars().run(cmd_line_clear_history)
        session = SQLManager.instance().get_session()
        self.assertEqual(session.query(Execution).count(), 0)

    def test_run_target_rule(self):
        # SQLManager.instance().create_all()
        cmd_line = ["python", "-D", self.__db_url, "-w", self.__example_def_file1, "-vv", "--until", "rule3"]
        with self.assertRaises(SystemExit) as se:
           WopMars().run(cmd_line)
        self.assertEqual(se.exception.code, 0)

    def test_run_input_file_not_ready(self):
        # SQLManager.instance().create_all()
        cmd_line = ["python", "-D", self.__db_url, "-w", self.__example_def_file_input_not_ready, "-vv"]
        with self.assertRaises(SystemExit) as se:
           WopMars().run(cmd_line)
        self.assertEqual(se.exception.code, 1)

if __name__ == "__main__":
    unittest.main()


