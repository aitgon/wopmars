import sqlite3
from unittest import TestCase

import os
import shutil

from wopmars import WopMars
from wopmars.utils.OptionManager import OptionManager
from wopmars.utils.PathManager import PathManager
from wopmars.SQLManager import SQLManager

class TestExample(TestCase):

    def setUp(self):
        self.test_path = PathManager.get_test_path()  # Get tests path
        OptionManager.initial_test_setup()  # Set tests arguments
        self.db_url = OptionManager.instance()["--database"]
        self.db = self.db_url[10:]
        self.wopfile = os.path.join(PathManager.get_package_path(), "wopmars/example/wopexample/Wopfile.yml")
        self.working_directory = os.path.join(PathManager.get_package_path(), "wopmars/example/wopexample")
    #
    def tearDown(self):

        shutil.rmtree(os.path.join(self.test_path, "outdir_path"), ignore_errors=True)
        PathManager.unlink(self.db)
        OptionManager._drop()
        SQLManager._drop()

    def test_example(self):

        cmd_args = [None, "-v", "--database", self.db_url, "--wopfile", self.wopfile, "--directory", self.working_directory]
        with self.assertRaises(SystemExit) as se:
            WopMars().run(cmd_args)
        self.assertEqual(se.exception.code, 0)

        conn = sqlite3.connect(self.db)
        cursor = conn.execute("SELECT * FROM 'Piece';")
        row_list = sorted(cursor.fetchall())
        self.assertEqual(20, len(row_list))
        conn.close()
