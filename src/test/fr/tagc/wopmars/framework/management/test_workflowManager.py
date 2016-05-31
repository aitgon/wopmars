import os
import unittest
from unittest import TestCase

from fr.tagc.wopmars.framework.management.WorkflowManager import WorkflowManager
from fr.tagc.wopmars.utils.PathFinder import PathFinder
from fr.tagc.wopmars.utils.exceptions.WopMarsParsingException import WopMarsParsingException


class TestWorkflowManager(TestCase):

    # todo ask lionel comment gérer les différents cas de figure d'un singleton dans un test unitaire?
    def setUp(self):
        s_root_path = PathFinder.find_src(os.path.dirname(os.path.realpath(__file__)))
        s_path_to_example_definition_file = s_root_path + "resources/example_def_file3.yml"
        s_path_to_not_existing_example_definition_file = s_root_path + "definition_file_that_doesnt_exists.yml"
        s_path_to_wrong_example_definition_file_not_dag = s_root_path + "resources/example_def_file_not_a_dag.yml"

        self.__workflow_manager_wrong = WorkflowManager(s_path_to_wrong_example_definition_file_not_dag)
        try:
            self.__workflow_manager_right = WorkflowManager(s_path_to_example_definition_file)
        except:
            raise AssertionError('Should not raise exception')

        with self.assertRaises(SystemExit):
            WorkflowManager(s_path_to_not_existing_example_definition_file)

    def test_run(self):
        try:
            self.__workflow_manager_right.run()
        except:
            raise AssertionError('Should not raise exception')

        with self.assertRaises(SystemExit):
            self.__workflow_manager_wrong.run()

if __name__ == '__main__':
    unittest.main()

