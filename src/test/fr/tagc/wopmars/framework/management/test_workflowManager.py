import os
import unittest
from unittest import TestCase

import subprocess

from src.main.fr.tagc.wopmars.framework.bdd.SQLManager import SQLManager
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

    def tearDown(self):
        SQLManager.drop_all()
        os.remove("/home/giffon/Documents/wopmars/src/resources/output_File1.txt")
        os.remove("/home/giffon/Documents/wopmars/src/resources/output_File2.txt")
        os.remove("/home/giffon/Documents/wopmars/src/resources/output_File3.txt")
        os.remove("/home/giffon/Documents/wopmars/src/resources/output_File4.txt")
        os.remove("/home/giffon/Documents/wopmars/src/resources/output_File5.txt")
        os.remove("/home/giffon/Documents/wopmars/src/resources/output_File6.txt")
        os.remove("/home/giffon/Documents/wopmars/src/resources/output_File7.txt")

    def test_run(self):
        OptionManager.instance()["--dot"] = None

        with self.assertRaises(SystemExit):
            self.__finishing_wm.run()

        with self.assertRaises(WopMarsException):
            self.__error_wm.run()


if __name__ == '__main__':
    unittest.main()

