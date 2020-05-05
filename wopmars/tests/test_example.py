import pathlib
import sqlite3
from unittest import TestCase

import os
import shutil

from wopmars import WopMars, OptionManager, SQLManager
from wopmars.utils.OptionManager import OptionManager
from wopmars.utils.PathManager import PathManager
from wopmars.SQLManager import SQLManager

class TestExample(TestCase):

    def setUp(self):
        self.test_path = PathManager.get_test_path()  # Get tests path
        OptionManager.initial_test_setup()  # Set tests arguments
        self.__db_url = OptionManager.instance()["--database"]
        PathManager.unlink(self.__db_url)
        self.__db_url = OptionManager.instance()["--database"]
        self.__db_path = self.__db_url[10:]
        self.__example_def_file1 = os.path.join(PathManager.get_package_path(), "wopmars/example/wopexample/Wopfile.yml")
        self.wopmars_example_dir_path = os.path.join(PathManager.get_package_path(), "wopmars/example/wopexample")

    # def setUp(self):
    #     self.__cwd = os.getcwd()
    #     self.outdir_path = os.path.join(self.test_path, "outdir")
    #     pathlib.Path(self.outdir_path).mkdir(parents=True, exist_ok=True)
    #     self.wopexample_test_dir_path = os.path.join(self.outdir_path, "wopexample")
    #
    def tearDown(self):

        shutil.rmtree(os.path.join(self.test_path, "outdir"), ignore_errors=True)
        PathManager.unlink(self.__db_url)
        OptionManager._drop()
        SQLManager._drop()

    def test_example0(self):

        cmd_line = ["python", "-D", self.__db_url, "-w", self.__example_def_file1, "-v", "-d", self.wopmars_example_dir_path]
        with self.assertRaises(SystemExit) as se:
            WopMars().run(cmd_line)
        self.assertEqual(se.exception.code, 0)

        conn = sqlite3.connect(self.__db_path)
        cursor = conn.execute("SELECT * FROM 'Piece';")
        row_list = sorted(cursor.fetchall())
        self.assertEqual(20, len(row_list))
        conn.close()


    # def test_example(self):
    #
    #     ################################################################################################################
    #     #
    #     # Create example, change and install example
    #     #
    #     ################################################################################################################
    #
    #     cmd = "wopmars example -d {}".format(self.outdir_path)
    #     cmd_args_list = shlex.split(cmd)
    #     subprocess.run(cmd_args_list)
    #
    #     os.chdir(self.wopexample_test_dir_path)
    #     # import pdb; pdb.set_trace()
    #     pip.main(['install', '.', '--upgrade', '-q'])  # not working in travis
    #     # subprocess.run(shlex.split("python -m pip install ."))  # not working in travis
    #
    #     ################################################################################################################
    #     #
    #     # Run example
    #     #
    #     ################################################################################################################
    #
    #     sqlite_path = os.path.join(self.wopexample_test_dir_path, "db.sqlite")
    #     wopfile_path = os.path.join(PathManager.get_package_path(), "wopmars/example/wopexample/Wopfile.yml")
    #     cmd = "wopmars -w {} -D sqlite:///{} -v -d {}".format(wopfile_path, sqlite_path, self.wopexample_test_dir_path)
    #     # import pdb; pdb.set_trace()
    #     cmd_args_list = shlex.split(cmd)
    #     print("Get cwd:", os.getcwd())
    #     # import pdb; pdb.set_trace()
    #     subprocess.run(cmd_args_list)
    #     # print("Sqlite path:", sqlite_path)
    #
    #     # The ORM method does not work in Travis
    #     # import pdb; pdb.set_trace()
    #     conn = sqlite3.connect(sqlite_path)
    #     cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table';")
    #     table_list = sorted(cursor.fetchall())
    #     print(table_list)
    #     print(len(table_list))
    #     # cursor = conn.execute('select * from Piece;')
    #     self.assertEqual(9, len(table_list))
    #     # self.assertEqual(sorted(table_list), [('Piece',), ('PieceCar',), ('wom_Execution',),
    #     #                               ('wom_FileInputOutputInformation',), ('wom_Option',),
    #     #                               ('wom_TableInputOutputInformation',), ('wom_TableModificationTime',),
    #     #                               ('wom_ToolWrapper',), ('wom_TypeInputOrOutput',)])
    #     conn.close()
