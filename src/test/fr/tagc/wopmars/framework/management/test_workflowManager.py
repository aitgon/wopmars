import os
import unittest
from unittest import TestCase

import subprocess

from FooBase import FooBase
from FooWrapper12 import FooWrapper12
from FooWrapper9 import FooWrapper9
from src.main.fr.tagc.wopmars.framework.bdd.SQLManager import SQLManager
from src.main.fr.tagc.wopmars.framework.bdd.tables import IOFilePut
from src.main.fr.tagc.wopmars.framework.bdd.tables.IODbPut import IODbPut
from src.main.fr.tagc.wopmars.framework.bdd.tables.IOFilePut import IOFilePut
from src.main.fr.tagc.wopmars.framework.bdd.tables.Type import Type
from src.main.fr.tagc.wopmars.framework.management.WorkflowManager import WorkflowManager
from src.main.fr.tagc.wopmars.utils.OptionManager import OptionManager
from src.main.fr.tagc.wopmars.utils.PathFinder import PathFinder
from src.main.fr.tagc.wopmars.utils.exceptions.WopMarsException import WopMarsException


class TestWorkflowManager(TestCase):

    def setUp(self):
        OptionManager.initial_test_setup()
        SQLManager.create_all()
        s_root_path = PathFinder.find_src(os.path.dirname(os.path.realpath(__file__)))

        s_path_to_example_definition_file_finishing = s_root_path + "resources/example_def_file.yml"
        s_path_to_example_definition_file_that_end_with_error = \
            s_root_path + \
            "resources/example_def_file_toolwrapper_never_ready.yml"

        OptionManager.instance()["DEFINITION_FILE"] = s_path_to_example_definition_file_finishing
        self.__finishing_wm = WorkflowManager()

        OptionManager.instance()["DEFINITION_FILE"] = s_path_to_example_definition_file_that_end_with_error
        self.__error_wm = WorkflowManager()

    def test_erase_output(self):
        s_root_path = PathFinder.find_src(os.path.realpath(__file__))

        test_out_file_path = s_root_path + "resources/outputs/output_Filetest_erase.txt"
        session = SQLManager.instance().get_session()
        for i in range(10):
            f = FooBase(name="testworkflowmanager" + str(i))
            session.add(f)
        session.commit()

        p = subprocess.Popen(["touch", test_out_file_path])
        p.wait()

        output_entry = Type(name="output")

        f1 = IOFilePut(name="output1", path=test_out_file_path)
        f1.type = output_entry
        t1 = IODbPut(name="FooBase")
        t1.type = output_entry
        tw = FooWrapper12(rule_name="testworkflowmanager")
        tw.files.extend([f1])
        tw.tables.extend([t1])

        self.__finishing_wm.erase_output(tw)

        self.assertEqual(len(session.query(FooBase).all()), 0)
        self.assertFalse(os.path.exists(test_out_file_path))

        session.rollback()

    def tearDown(self):
        SQLManager.drop_all()
        PathFinder.dir_content_remove("resources/outputs/")
        OptionManager._drop()
        SQLManager._drop()

    def test_run(self):
        OptionManager.instance()["--dot"] = None

        with self.assertRaises(SystemExit):
            self.__finishing_wm.run()

        with self.assertRaises(WopMarsException):
            self.__error_wm.run()


if __name__ == '__main__':
    unittest.main()

