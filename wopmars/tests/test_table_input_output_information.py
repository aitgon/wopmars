import shutil
import unittest
from unittest import TestCase

from wopmars.tests.resource.model.FooBase import FooBase
from wopmars.tests.resource.model.FooBase2 import FooBase2
from wopmars.SQLManager import SQLManager
from wopmars.models.TableInputOutputInformation import TableInputOutputInformation
from wopmars.utils.OptionManager import OptionManager
from wopmars.utils.PathManager import PathManager


class TestTableInputOutputInformation(TestCase):

    def setUp(self):

        self.test_path = PathManager.get_test_path()
        OptionManager.initial_test_setup()  # Set tests arguments
        SQLManager.instance().create_all()  # Create database with tables

        self.__local_session = SQLManager.instance().get_session()
        try:
            for i in range(10):
                self.__local_session.add(FooBase(name="testIODB " + str(i)))
            self.__local_session.commit()
        except Exception as e:
            self.__local_session.rollback()
            self.__local_session.close()
            raise e

        self.__io_base_existing = TableInputOutputInformation(model_py_path="FooBase", table_key="FooBase", table_name="FooBase")
        self.__io_base_existing.set_table(FooBase)
        self.__io_base_existing2 = TableInputOutputInformation(model_py_path="FooBase", table_key="FooBase", table_name="FooBase")
        self.__io_base_existing2.set_table(FooBase)
        self.__io_base_existing3 = TableInputOutputInformation(model_py_path="FooBase2", table_key="FooBase2", table_name="FooBase2")
        self.__io_base_existing3.set_table(FooBase2)

    def tearDown(self):
        SQLManager.instance().get_session().close()
        SQLManager.instance().drop_all()
        # PathManager.dir_content_remove(os.path.join(self.test_path, "outdir"))
        shutil.rmtree("outdir", ignore_errors=True)
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
