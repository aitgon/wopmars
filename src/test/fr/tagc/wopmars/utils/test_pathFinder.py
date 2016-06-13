import unittest
from unittest import TestCase

from src.main.fr.tagc.wopmars.utils.PathFinder import PathFinder


class TestPathFinder(TestCase):
    def test_find_src(self):
        self.assertEqual(PathFinder.find_src("/home/user/src/toto/tata"), "/home/user/src/")

    def test_check_valid_path(self):
        self.assertIsNone(PathFinder.check_valid_path(None))
        self.assertRaises(FileNotFoundError, PathFinder.check_valid_path, ("/coucou/toto"))
        self.assertEqual(PathFinder.check_valid_path("/tmp/test"), "/tmp/test")


if __name__ == '__main__':
    unittest.main()