import unittest
from unittest import TestCase

from wopmars.utils.PathManager import PathManager


class TestPathFinder(TestCase):
    #def test_find_src(self):
    #    self.assertEqual(PathManager.get_package_path("/home/user/wopmars/toto/tata"), "/home/user/wopmars/")

    def test_check_valid_path(self):
        self.assertIsNone(PathManager.check_valid_path(None))
        self.assertRaises(FileNotFoundError, PathManager.check_valid_path, ("/coucou/toto"))
        self.assertEqual(PathManager.check_valid_path("/tmp/test_bak"), "/tmp/test_bak")


if __name__ == '__main__':
    unittest.main()
