from unittest import TestCase

import os
import pathlib
import pip
import shlex
import shutil
import sqlalchemy
import subprocess
import sqlite3

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

        sqlite_path = "db.sqlite"
        cmd = "wopmars -w Wopfile.yml -D sqlite:///db.sqlite".format(sqlite_path)
        # import pdb; pdb.set_trace()
        cmd_args_list = shlex.split(cmd)
        subprocess.run(cmd_args_list)

        # from wopmars.example.wopexample.model.Piece import Piece
        # test_engine = sqlalchemy.create_engine('sqlite:///{}'.format(sqlite_path), echo=False)
        # test_session = (sqlalchemy.orm.sessionmaker(bind=test_engine))()
        # self.assertEqual(20, test_session.query(Piece).order_by(Piece.id).count())

        # import pdb; pdb.set_trace()
        # The ORM method does not work in Travis
        conn = sqlite3.connect(sqlite_path)
        cursor = conn.execute('select * from piece;')
        self.assertEqual(20, len(cursor.fetchall()))
        conn.close()

