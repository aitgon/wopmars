import unittest
from unittest import TestCase

from FooBase import FooBase
from FooBase2 import FooBase2
from src.main.fr.tagc.wopmars.framework.bdd.SQLManager import SQLManager
from src.main.fr.tagc.wopmars.framework.bdd.tables.IODbPut import IODbPut
from src.main.fr.tagc.wopmars.framework.bdd.tables.IOFilePut import IOFilePut
from src.main.fr.tagc.wopmars.framework.bdd.tables.Option import Option
from src.main.fr.tagc.wopmars.framework.bdd.tables.ToolWrapper import ToolWrapper
from src.main.fr.tagc.wopmars.framework.bdd.tables.Type import Type
from src.main.fr.tagc.wopmars.utils.OptionManager import OptionManager
from src.main.fr.tagc.wopmars.utils.PathFinder import PathFinder


class TestIODbPut(TestCase):
    def setUp(self):
        OptionManager.initial_test_setup()
        print(OptionManager.instance()["--log"])

        SQLManager.instance().create_all()
        self.__local_session = SQLManager.instance().get_session()
        try:
            for i in range(10):
                self.__local_session.add(FooBase(name="testIODB " + str(i)))
            self.__local_session.commit()
        except Exception as e:
            self.__local_session.rollback()
            self.__local_session.close()
            raise e

        self.__io_base_existing = IODbPut(name="FooBase")
        self.__io_base_existing.set_table(FooBase)
        self.__io_base_existing2 = IODbPut(name="FooBase")
        self.__io_base_existing2.set_table(FooBase)
        self.__io_base_existing3 = IODbPut(name="FooBase2")
        self.__io_base_existing3.set_table(FooBase2)

    def tearDown(self):
        SQLManager.instance().drop_all()
        PathFinder.dir_content_remove("resources/outputs/")
        OptionManager._drop()
        SQLManager._drop()

    def test_eq(self):
        self.assertEqual(self.__io_base_existing, self.__io_base_existing2)
        self.assertNotEqual(self.__io_base_existing, self.__io_base_existing3)

    def test_is_ready(self):
        self.assertTrue(self.__io_base_existing.is_ready())
        self.assertFalse(self.__io_base_existing3.is_ready())

if __name__ == "__main__":
    unittest.main()
