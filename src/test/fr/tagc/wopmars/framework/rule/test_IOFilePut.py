import os
import unittest
from unittest import TestCase

from src.main.fr.tagc.wopmars.framework.rule.IOFilePut import IOFilePut
from src.main.fr.tagc.wopmars.utils.PathFinder import PathFinder


class TestIOFilePut(TestCase):
    def setUp(self):
        s_root_path = PathFinder.find_src(os.path.dirname(os.path.realpath(__file__)))
        s_path_to_example_existing_file = s_root_path + "resources/example_existing_file.txt"
        s_path_to_example_existing_file2 = s_root_path + "resources/example_existing_file2.txt"
        s_path_to_example_not_existing_file = s_root_path + "resources/example_not_existing_file.txt"

        self.__io_file_existing = IOFilePut("existing_file", s_path_to_example_existing_file)
        self.__io_file_existing2 = IOFilePut("existing_file", s_path_to_example_existing_file)
        self.__io_file_existing3 = IOFilePut("existing_file", s_path_to_example_existing_file2)
        self.__io_file_not_existing = IOFilePut("not_existing_file", s_path_to_example_not_existing_file)

    def test_is_ready(self):
        self.assertTrue(self.__io_file_existing.is_ready())
        self.assertFalse(self.__io_file_not_existing.is_ready())

    def test_eq(self):
        self.assertEqual(self.__io_file_existing, self.__io_file_existing2)
        self.assertNotEqual(self.__io_file_existing, self.__io_file_existing3)

if __name__ == "__main__":
    unittest.main()