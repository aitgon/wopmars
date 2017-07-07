import unittest
from unittest import TestCase

from wopmars.framework.database.tables.IOFilePut import IOFilePut
from wopmars.utils.SetUtils import SetUtils


class TestSetUtils(TestCase):
    def setUp(self):
        # 1 in 2 but not 2 in 1
        self.__set1 = set("a")
        self.__set2 = set(("a", "b"))

    def test_all_elm_of_one_set_in_one_other(self):
        self.assertTrue(SetUtils.all_elm_of_one_set_in_one_other(self.__set1, self.__set2))
        self.assertFalse(SetUtils.all_elm_of_one_set_in_one_other(self.__set2, self.__set1))

if __name__ == "__main__":
    unittest.main()