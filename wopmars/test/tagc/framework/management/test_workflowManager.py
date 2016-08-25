import os
import unittest
from unittest import TestCase

import subprocess

from FooBase import FooBase
from FooWrapper12 import FooWrapper12
from FooWrapper9 import FooWrapper9
from wopmars.main.tagc.framework.bdd.SQLManager import SQLManager
from wopmars.main.tagc.framework.bdd.tables import IOFilePut
from wopmars.main.tagc.framework.bdd.tables.IODbPut import IODbPut
from wopmars.main.tagc.framework.bdd.tables.IOFilePut import IOFilePut
from wopmars.main.tagc.framework.bdd.tables.Type import Type
from wopmars.main.tagc.framework.management.WorkflowManager import WorkflowManager
from wopmars.main.tagc.utils.OptionManager import OptionManager
from wopmars.main.tagc.utils.PathFinder import PathFinder
from wopmars.main.tagc.utils.exceptions.WopMarsException import WopMarsException


class TestWorkflowManager(TestCase):

    def setUp(self):
        OptionManager.initial_test_setup()
        SQLManager.instance().create_all()
        s_root_path = PathFinder.find_src(os.path.dirname(os.path.realpath(__file__)))

        self.__s_path_to_example_definition_file_finishing = s_root_path + "resources/example_def_file.yml"
        self.__s_path_to_example_definition_file_that_end_with_error = \
            s_root_path + \
            "resources/example_def_file_toolwrapper_never_ready.yml"

        self.__wm = WorkflowManager()


    def test_erase_output(self):
        #todo
        pass

    def tearDown(self):
        SQLManager.instance().drop_all()
        PathFinder.dir_content_remove("resources/outputs/")
        OptionManager._drop()
        SQLManager._drop()

    def test_run(self):
        # OptionManager.instance()["--dot"] = None
        #
        # OptionManager.instance()["--wopfile"] = self.__s_path_to_example_definition_file_finishing
        # with self.assertRaises(SystemExit):
        #     self.__wm.run()

        OptionManager.instance()["--wopfile"] = self.__s_path_to_example_definition_file_that_end_with_error
        with self.assertRaises(WopMarsException):
            self.__wm.run()

if __name__ == '__main__':
    unittest.main()
