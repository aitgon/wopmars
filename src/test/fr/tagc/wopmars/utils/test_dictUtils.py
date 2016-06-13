import unittest
from unittest import TestCase

from src.main.fr.tagc.wopmars.framework.rule.IOFilePut import IOFilePut
from src.main.fr.tagc.wopmars.utils.DictUtils import DictUtils


class TestDictUtils(TestCase):
    def setUp(self):
        # elements from 1 ar in 2
        self.__dict1 = {"a": IOFilePut("name1", "path1"), "b": IOFilePut("name2", "path2")}
        self.__dict2 = {"a": IOFilePut("name1", "path1"), "b": IOFilePut("name2", "path2"), "c":IOFilePut("name3", "path3")}

        # the value of the element of 3 is in 1
        self.__dict3 = {"d": IOFilePut("name5", "path1")}

        # the name is the same but the value is different than 1
        self.__dict4 = {"a": IOFilePut("name1", "path6")}

    def test_elm_of_one_dict_in_one_other(self):
        self.assertTrue(DictUtils.elm_of_one_dict_in_one_other(self.__dict1, self.__dict2))
        self.assertFalse(DictUtils.elm_of_one_dict_in_one_other(self.__dict2, self.__dict1))

    def test_at_least_one_value_of_one_in_an_other(self):
        self.assertTrue(DictUtils.at_least_one_value_of_one_in_an_other(self.__dict1, self.__dict3))
        self.assertFalse(DictUtils.at_least_one_value_of_one_in_an_other(self.__dict1, self.__dict4))

if __name__ == '__main__':
    unittest.main()