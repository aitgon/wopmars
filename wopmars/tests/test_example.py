import os
import shutil
import sqlite3
import subprocess
import sys

from unittest import TestCase
from wopmars import WopMars
from wopmars.SQLManager import SQLManager
from wopmars.utils.OptionManager import OptionManager
from wopmars.utils.PathManager import PathManager


class TestExample(TestCase):

    def setUp(self):
        self.test_path = PathManager.get_test_path()  # Get tests path
        OptionManager.initial_test_setup()  # Set tests arguments
        self.db_url = OptionManager.instance()["--database"]
        self.db = self.db_url[10:]
        self.example_dir_path = os.path.join(PathManager.get_package_path(), "data/example")
        self.wopfile = os.path.join(self.example_dir_path, "Wopfile.yml")
        self.working_directory = os.path.join(PathManager.get_package_path(), "data/example")
    #
    def tearDown(self):
        # pass
        # pip.main(['uninstall', 'wopexamplecar', '-y']) # working in travis
        subprocess.run([sys.executable, '-m', 'pip', 'uninstall', 'example', '-y'])
        shutil.rmtree(os.path.join(self.working_directory, "build"), ignore_errors=True)
        shutil.rmtree(os.path.join(self.working_directory, "wopexamplecar.egg-info"), ignore_errors=True)
        PathManager.unlink(self.db)
        OptionManager._drop()
        SQLManager._drop()

    def test_example(self):
        # pip.main(['install', '{}/.'.format(self.example_dir_path), '--upgrade']) # working in travis
        subprocess.run([sys.executable, '-m', 'pip', 'install', '{}/.'.format(self.example_dir_path), '--upgrade'])
        cmd_args = [None, "-v", "--database", self.db_url, "--wopfile", self.wopfile, "--directory", self.working_directory]
        with self.assertRaises(SystemExit) as se:
            WopMars().run(cmd_args)
        self.assertEqual(se.exception.code, 0)

        conn = sqlite3.connect(self.db)
        cursor = conn.execute("SELECT * FROM 'Piece';")
        row_list = sorted(cursor.fetchall())
        self.assertEqual(20, len(row_list))
        conn.close()
