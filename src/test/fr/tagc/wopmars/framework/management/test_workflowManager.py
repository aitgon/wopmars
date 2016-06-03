import os
import unittest
from unittest import TestCase

from fr.tagc.wopmars.framework.management.WorkflowManager import WorkflowManager
from fr.tagc.wopmars.utils.OptionManager import OptionManager
from fr.tagc.wopmars.utils.PathFinder import PathFinder
from fr.tagc.wopmars.utils.exceptions.WopMarsException import WopMarsException


class TestWorkflowManager(TestCase):

    def setUp(self):
        OptionManager({'-v': 1, 'DEFINITION_FILE': None, "--dot": None})
        s_root_path = PathFinder.find_src(os.path.dirname(os.path.realpath(__file__)))

        s_path_to_example_definition_file_finishing = s_root_path + "resources/example_def_file3.yml"
        s_path_to_example_definition_file_that_end_with_error = \
            s_root_path + \
            "resources/example_def_file_toolwrapper_never_ready.yml"

        OptionManager()["DEFINITION_FILE"] = s_path_to_example_definition_file_finishing
        self.__finishing_wm = WorkflowManager()

        OptionManager()["DEFINITION_FILE"] = s_path_to_example_definition_file_that_end_with_error
        self.__error_wm = WorkflowManager()

    def test_run(self):
        with self.assertRaises(SystemExit):
            self.__finishing_wm.run()

        with self.assertRaises(WopMarsException):
            self.__error_wm.run()

if __name__ == '__main__':
    unittest.main()

