import unittest
from unittest import TestCase

from FooBase2 import FooBase2

from src.main.fr.tagc.wopmars.framework.rule.IODbPut import IODbPut
from FooBase import FooBase


class TestIODbPut(TestCase):
    def setUp(self):


        self.__io_base_existing = IODbPut(FooBase)
        self.__io_base_existing2 = IODbPut(FooBase)
        self.__io_base_existing3 = IODbPut(FooBase2)

    def test_eq(self):
        self.assertEqual(self.__io_base_existing, self.__io_base_existing2)
        self.assertNotEqual(self.__io_base_existing, self.__io_base_existing3)

    def test_is_ready(self):
        self.assertTrue(self.__io_base_existing.is_ready())
        self.assertFalse(self.__io_base_existing3.is_ready())

if __name__ == "__main__":
    unittest.main()
