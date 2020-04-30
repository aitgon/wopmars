import os
import unittest
from unittest import TestCase

from wopmars.SQLManager import SQLManager
from wopmars.models.FileInputOutputInformation import FileInputOutputInformation
from wopmars.utils.OptionManager import OptionManager
from wopmars.utils.PathManager import PathManager


class TestFileInputOutputInformation(TestCase):
    def setUp(self):
        OptionManager.initial_test_setup()

        self.s_root_path = PathManager.get_module_path()
        s_path_to_example_existing_file = os.path.join(self.s_root_path, "test/resource/input_files/example_existing_file.txt")
        s_path_to_example_existing_file2 = os.path.join(self.s_root_path, "test/resource/input_files/example_existing_file2.txt")
        s_path_to_example_not_existing_file = os.path.join(self.s_root_path, "test/resource/input_files/example_not_existing_file.txt")

        self.__io_file_existing = FileInputOutputInformation(file_key="existing_file", path=s_path_to_example_existing_file)
        self.__io_file_existing2 = FileInputOutputInformation(file_key="existing_file", path=s_path_to_example_existing_file)
        self.__io_file_existing3 = FileInputOutputInformation(file_key="existing_file2", path=s_path_to_example_existing_file)
        self.__io_file_existing4 = FileInputOutputInformation(file_key="existing_file", path=s_path_to_example_existing_file2)
        self.__io_file_not_existing = FileInputOutputInformation(file_key="not_existing_file", path=s_path_to_example_not_existing_file)

    def test_is_ready(self):
        self.assertTrue(self.__io_file_existing.is_ready())
        self.assertFalse(self.__io_file_not_existing.is_ready())

    def test_eq(self):
        self.assertEqual(self.__io_file_existing, self.__io_file_existing2)
        self.assertNotEqual(self.__io_file_existing, self.__io_file_existing3)
        self.assertNotEqual(self.__io_file_existing, self.__io_file_existing4)
        self.assertNotEqual(self.__io_file_existing, self.__io_file_not_existing)

    def tearDown(self):
        SQLManager.instance().get_session().close()
        SQLManager.instance().drop_all()
        PathManager.dir_content_remove(os.path.join(self.s_root_path, "test/output"))
        OptionManager._drop()
        SQLManager._drop()

if __name__ == "__main__":
    unittest.main()
