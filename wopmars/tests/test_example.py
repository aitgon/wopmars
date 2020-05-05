import logging
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
        self.wopexample_test_dir_path = os.path.join(self.outdir_path, "wopexample")

    def tearDown(self):

        # subprocess.run(shlex.split("python -m pip uninstall wopexamplecar -y"))
        # import pdb; pdb.set_trace()
        shutil.rmtree(self.outdir_path, ignore_errors=False)
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

        os.chdir(self.wopexample_test_dir_path)
        # import pdb; pdb.set_trace()
        pip.main(['install', '.', '--upgrade', '-q'])  # not working in travis
        # subprocess.run(shlex.split("python -m pip install ."))  # not working in travis

        ################################################################################################################
        #
        # Run example
        #
        ################################################################################################################

        sqlite_path = os.path.join(self.wopexample_test_dir_path, "db.sqlite")
        wopfile_path = os.path.join(PathManager.get_package_path(), "wopmars/example/wopexample/Wopfile.yml")
        cmd = "wopmars -w {} -D sqlite:///{} -v -d {}".format(wopfile_path, sqlite_path, self.wopexample_test_dir_path)
        # import pdb; pdb.set_trace()
        cmd_args_list = shlex.split(cmd)
        print("Get cwd:", os.getcwd())
        # import pdb; pdb.set_trace()
        subprocess.run(cmd_args_list)
        # print("Sqlite path:", sqlite_path)

        # The ORM method does not work in Travis
        # import pdb; pdb.set_trace()
        conn = sqlite3.connect(sqlite_path)
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table';")
        table_list = sorted(cursor.fetchall())
        print(table_list)
        print(len(table_list))
        # cursor = conn.execute('select * from Piece;')
        self.assertEqual(9, len(table_list))
        # self.assertEqual(sorted(table_list), [('Piece',), ('PieceCar',), ('wom_Execution',),
        #                               ('wom_FileInputOutputInformation',), ('wom_Option',),
        #                               ('wom_TableInputOutputInformation',), ('wom_TableModificationTime',),
        #                               ('wom_ToolWrapper',), ('wom_TypeInputOrOutput',)])
        conn.close()
