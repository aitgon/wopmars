import unittest
from unittest import TestCase

from src.main.fr.tagc.wopmars.base.FooBase import FooBase
from src.main.fr.tagc.wopmars.base.FooBase2 import FooBase2
from src.main.fr.tagc.wopmars.framework.rule.IODbPut import IODbPut
from src.main.fr.tagc.wopmars.framework.rule.ObjectSet import ObjectSet


class TestObjectSet(TestCase):
    def setUp(self):

        self.__obj_set_int1 = ObjectSet(range(5))
        self.__obj_set_int2 = ObjectSet(range(5))
        self.__obj_set_int3 = ObjectSet(range(4))

        self.__obj_set1 = ObjectSet()
        self.__obj_set1.add((
            IODbPut(FooBase()),
            IODbPut(FooBase()),
            IODbPut(FooBase2()),
        ))

        self.__obj_set2 = ObjectSet()
        self.__obj_set2.add((
            IODbPut(FooBase()),
            IODbPut(FooBase()),
            IODbPut(FooBase2()),
        ))

        self.__obj_set3 = ObjectSet()
        self.__obj_set3.add((
            IODbPut(FooBase()),
            IODbPut(FooBase2()),
            IODbPut(FooBase2()),
        ))

    def test_eq(self):
        self.assertEqual(self.__obj_set_int1, self.__obj_set_int2)
        self.assertNotEqual(self.__obj_set_int1, self.__obj_set_int3)

        self.assertEqual(self.__obj_set1, self.__obj_set2)
        self.assertNotEqual(self.__obj_set1, self.__obj_set3)

if __name__ == '__main__':
    unittest.main()
