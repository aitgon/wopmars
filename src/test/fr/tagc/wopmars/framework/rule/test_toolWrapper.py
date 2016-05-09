import unittest
from unittest import TestCase

from src.main.fr.tagc.wopmars.framework.rule.IOFilePut import IOFilePut
from src.main.fr.tagc.wopmars.framework.rule.ToolWrapper import ToolWrapper


class TestToolWrapper(TestCase):
    def setUp(self):
        self.__toolwrapper1 = ToolWrapper({"input1": IOFilePut("input1", "file1.txt")},
                                          {"output1": IOFilePut("output1", "file2.txt")},
                                          {"param1": IOFilePut("param1", 1)})

        self.__toolwrapper2 = ToolWrapper({"input1": IOFilePut("input1", "file1.txt")},
                                          {"output1": IOFilePut("output1", "file2.txt")},
                                          {"param1": IOFilePut("param1", 1)})

        self.__toolwrapper3 = ToolWrapper({"input1": IOFilePut("input1", "file1.txt")},
                                          {"output1": IOFilePut("output1", "file2.txt")},
                                          {"param1": IOFilePut("param1", 3)})

    def test_eq(self):
        self.assertEqual(self.__toolwrapper1, self.__toolwrapper2)
        self.assertNotEqual(self.__toolwrapper1, self.__toolwrapper3)

if __name__ == '__main__':
    unittest.main()
