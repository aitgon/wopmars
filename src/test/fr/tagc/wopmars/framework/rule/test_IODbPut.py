import unittest
from unittest import TestCase

from FooBase2 import FooBase2
from src.main.fr.tagc.wopmars.framework.bdd.SQLManager import SQLManager

from src.main.fr.tagc.wopmars.framework.rule.IODbPut import IODbPut
from FooBase import FooBase
from src.main.fr.tagc.wopmars.utils.OptionManager import OptionManager


class TestIODbPut(TestCase):
    def setUp(self):
        OptionManager()["-v"] = 4
        self.__local_session = SQLManager.instance().get_session()
        try:
            for i in range(10):
                self.__local_session.add(FooBase(name="testIODB " + str(i)))
            self.__local_session.commit()
        except Exception as e:
            self.__local_session.rollback()
            self.__local_session.close()
            raise e

        self.__io_base_existing = IODbPut(FooBase)
        self.__io_base_existing2 = IODbPut(FooBase)
        self.__io_base_existing3 = IODbPut(FooBase2)

    def tearDown(self):
        foo_objects = self.__local_session.query(FooBase).filter(FooBase.name.like('string %')).all()
        for obj in foo_objects:
            self.__local_session.delete(obj)
        self.__local_session.commit()
        self.__local_session.close()

    def test_eq(self):
        self.assertEqual(self.__io_base_existing, self.__io_base_existing2)
        self.assertNotEqual(self.__io_base_existing, self.__io_base_existing3)

    def test_is_ready(self):
        self.assertTrue(self.__io_base_existing.is_ready())
        self.assertFalse(self.__io_base_existing3.is_ready())

if __name__ == "__main__":
    unittest.main()
