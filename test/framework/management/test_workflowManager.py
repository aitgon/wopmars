import os
import unittest
from unittest import TestCase

from wopmars.framework.database.SQLManager import SQLManager
from wopmars.framework.management.WorkflowManager import WorkflowManager
from wopmars.utils.OptionManager import OptionManager
from wopmars.utils.PathFinder import PathFinder
from wopmars.utils.exceptions.WopMarsException import WopMarsException


class TestWorkflowManager(TestCase):

    def setUp(self):
        OptionManager.initial_test_setup()
        SQLManager.instance().create_all()
        s_root_path = PathFinder.get_module_path()

        self.__s_path_to_example_definition_file_finishing = os.path.join(s_root_path, "test/resource/wopfile/example_def_file1.yml")
        self.__s_path_to_example_definition_file_that_end_with_error = os.path.join(s_root_path, "test/resource/wopfile/example_def_file5_never_ready.yml")

        self.__wm = WorkflowManager()


    def test_erase_output(self):
        #todo LG
        pass

    def tearDown(self):
        SQLManager.instance().get_session().close()
        SQLManager.instance().drop_all()
        PathFinder.dir_content_remove("test/output")
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
