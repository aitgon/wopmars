import unittest
from unittest import TestCase

from wopmars.utils.PathFinder import PathFinder


class TestPathFinder(TestCase):
    #def test_find_src(self):
    #    self.assertEqual(PathFinder.get_module_path("/home/user/wopmars/toto/tata"), "/home/user/wopmars/")

    def test_check_valid_path(self):
        self.assertIsNone(PathFinder.check_valid_path(None))
        self.assertRaises(FileNotFoundError, PathFinder.check_valid_path, ("/coucou/toto"))
        self.assertEqual(PathFinder.check_valid_path("/tmp/test_bak"), "/tmp/test_bak")


if __name__ == '__main__':
    unittest.main()
