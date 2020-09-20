from unittest import TestCase
from wopmars.utils.PathManager import PathManager
import os
import tempfile
import unittest


class TestPathFinder(TestCase):

    def test_check_valid_path(self):
        self.assertIsNone(PathManager.check_valid_path(None))
        self.assertRaises(FileNotFoundError, PathManager.check_valid_path, ("/coucou/toto"))

        tempdir = os.path.join(tempfile.gettempdir(), 'test_bak')
        self.assertEqual(PathManager.check_valid_path(tempdir), tempdir)


if __name__ == '__main__':
    unittest.main()
