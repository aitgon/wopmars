import os
import unittest
from unittest import TestCase

from src.main.fr.tagc.wopmars.framework.bdd.SQLManager import SQLManager
from src.main.fr.tagc.wopmars.utils.PathFinder import PathFinder
from src.main.fr.tagc.wopmars.wopmars import WopMars


class TestWopMars(TestCase):
    def setUp(self):
        s_root_path = PathFinder.find_src(os.path.dirname(os.path.realpath(__file__)))

        self.__right_def_file = s_root_path + "resources/example_def_file.yml"

    def test_run(self):
        cmd_line = [self.__right_def_file, "-vvvv", "-n"]
        with self.assertRaises(SystemExit):
            WopMars().run(cmd_line)

    def tearDown(self):
        SQLManager.instance().drop_all()
        os.remove("/home/giffon/Documents/wopmars/src/resources/output_File1.txt")
        os.remove("/home/giffon/Documents/wopmars/src/resources/output_File2.txt")
        os.remove("/home/giffon/Documents/wopmars/src/resources/output_File3.txt")
        os.remove("/home/giffon/Documents/wopmars/src/resources/output_File4.txt")
        os.remove("/home/giffon/Documents/wopmars/src/resources/output_File5.txt")
        os.remove("/home/giffon/Documents/wopmars/src/resources/output_File6.txt")
        os.remove("/home/giffon/Documents/wopmars/src/resources/output_File7.txt")

if __name__ == "__main__":
    unittest.main()