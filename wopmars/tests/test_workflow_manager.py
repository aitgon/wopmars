import os
import shutil
import unittest
from unittest import TestCase

from wopmars.SQLManager import SQLManager
from wopmars.WorkflowManager import WorkflowManager
from wopmars.utils.OptionManager import OptionManager
from wopmars.utils.PathManager import PathManager
from wopmars.utils.WopMarsException import WopMarsException


class TestWorkflowManager(TestCase):

    def setUp(self):

        OptionManager.initial_test_setup()  # Set tests arguments
        SQLManager.instance().create_all()  # Create database with tables
        self.test_path = PathManager.get_test_path()

        self.__s_path_to_example_definition_file_finishing = os.path.join(
            self.test_path, "resource/wopfile/example_def_file1.yml")
        self.__s_path_to_example_definition_file_that_end_with_error = os.path.join(
            self.test_path, "resource/wopfile/example_def_file5_never_ready.yml")

        self.__workflow_manager = WorkflowManager()

    def tearDown(self):

        SQLManager.instance().get_session().close()
        SQLManager.instance().drop_all()
        shutil.rmtree(os.path.join(self.test_path, "outdir"), ignore_errors=True)
        OptionManager._drop()
        SQLManager._drop()

    def test_run(self):

        # OptionManager.instance()["--dot"] = None
        #
        # OptionManager.instance()["--wopfile"] = self.__s_path_to_example_definition_file_finishing
        # with self.assertRaises(SystemExit):
        #     self.__workflow_manager.run()

        OptionManager.instance()["--wopfile"] = self.__s_path_to_example_definition_file_that_end_with_error
        with self.assertRaises(WopMarsException):
            self.__workflow_manager.run()

if __name__ == '__main__':
    unittest.main()
