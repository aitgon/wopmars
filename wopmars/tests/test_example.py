from unittest import TestCase

import os
import pathlib
import pip
import shlex
import shutil
import subprocess
import sqlite3

from wopmars.utils.Logger import Logger
from wopmars.utils.PathManager import PathManager


class TestExample(TestCase):

    def setUp(self):
        self.__cwd = os.getcwd()
        self.test_path = PathManager.get_test_path()  # Get tests path
        self.outdir_path = os.path.join(self.test_path, "outdir")
        pathlib.Path(self.outdir_path).mkdir(parents=True, exist_ok=True)
        self.example_path = os.path.join(self.outdir_path, "wopexample")

    def tearDown(self):

        # subprocess.run(shlex.split("python -m pip uninstall wopexamplecar -y"))
        shutil.rmtree(self.example_path, ignore_errors=True)
        os.chdir(self.__cwd)

    def test_example(self):

        ################################################################################################################
        #
        # Create example, change and install example
        #
        ################################################################################################################

        cmd = "wopmars example -d {}".format(self.outdir_path)
        cmd_args_list = shlex.split(cmd)
        subprocess.run(cmd_args_list)
        os.chdir(self.example_path)
        # import pdb; pdb.set_trace()
        pip.main(['install', '.', '--upgrade', '-q'])  # not working in travis
        # subprocess.run(shlex.split("python -m pip install ."))  # not working in travis

        ################################################################################################################
        #
        # Run example
        #
        ################################################################################################################

        sqlite_path = os.path.join(self.outdir_path, "db.sqlite")
        cmd = "wopmars -w Wopfile.yml -D sqlite:///{} -v".format(sqlite_path)
        # import pdb; pdb.set_trace()
        cmd_args_list = shlex.split(cmd)
        subprocess.run(cmd_args_list)
        print("File exists", os.path.exists(sqlite_path))
        
        # The ORM method does not work in Travis
        conn = sqlite3.connect(sqlite_path)
        # cursor = conn.execute('select * from Piece;')
        # self.assertEqual(20, len(cursor.fetchall()))
        conn.close()


