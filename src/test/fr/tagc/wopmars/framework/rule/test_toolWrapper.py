import unittest
from unittest import TestCase

from src.main.fr.tagc.wopmars.framework.rule.IOFilePut import IOFilePut
from src.main.fr.tagc.wopmars.framework.rule.Option import Option
from src.main.fr.tagc.wopmars.framework.rule.ToolWrapper import ToolWrapper
from src.main.fr.tagc.wopmars.toolwrappers.FooWrapper3 import FooWrapper3
from src.main.fr.tagc.wopmars.utils.exceptions.WopMarsParsingException import WopMarsParsingException


class TestToolWrapper(TestCase):
    def setUp(self):
        self.__toolwrapper1 = ToolWrapper({"input1": IOFilePut("input1", "file1.txt")},
                                          {"output1": IOFilePut("output1", "file2.txt")},
                                          {"param1": Option("param1", 1)})

        self.__toolwrapper2 = ToolWrapper({"input1": IOFilePut("input1", "file1.txt")},
                                          {"output1": IOFilePut("output1", "file2.txt")},
                                          {"param1": Option("param1", 1)})

        self.__toolwrapper3 = ToolWrapper({"input1": IOFilePut("input1", "file1.txt")},
                                          {"output1": IOFilePut("output1", "file2.txt")},
                                          {"param1": Option("param1", 3)})

        self.__foowrapper_right = FooWrapper3({"input1": IOFilePut("input1", "file1.txt")},
                                              {"output1": IOFilePut("output1", "file2.txt")},
                                              {"param1": Option("param1", 3)})

        self.__foowrapper_wrong1 = FooWrapper3({"failure": IOFilePut("input1", "file1.txt")},
                                               {"output1": IOFilePut("output1", "file2.txt")},
                                               {"param1": Option("param1", 3)})

        self.__foowrapper_wrong2 = FooWrapper3({"input1": IOFilePut("input1", "file1.txt"),
                                                "input2": IOFilePut("input2", "file1.txt")},
                                               {"output1": IOFilePut("output1", "file2.txt")},
                                               {"param1": Option("param1", 3)})

        self.__foowrapper_wrong3 = FooWrapper3({"input1": IOFilePut("input1", "file1.txt")},
                                               {"output1": IOFilePut("output1", "file2.txt")},
                                               {"failure": Option("failure", 3)})

        self.__foowrapper_wrong4 = FooWrapper3({"input1": IOFilePut("input1", "file1.txt")},
                                               {"output1": IOFilePut("output1", "file2.txt")},
                                               {"param1": Option("param1", "failure")})

        self.__foowrapper_wrong5 = FooWrapper3({"input1": IOFilePut("input1", "file1.txt")},
                                              {"output1": IOFilePut("output1", "file2.txt")},
                                              {})

        self.__toolwrapper_first = ToolWrapper({"input1": IOFilePut("input1", "file1.txt")},
                                               {"output1": IOFilePut("output1", "file2.txt")},
                                               {})

        self.__toolwrapper_second = ToolWrapper({"input1": IOFilePut("input1", "file2.txt")},
                                                {"output1": IOFilePut("output1", "file3.txt")},
                                                {})

    def test_eq(self):
        self.assertEqual(self.__toolwrapper1, self.__toolwrapper2)
        self.assertNotEqual(self.__toolwrapper1, self.__toolwrapper3)

    def test_is_content_respected(self):
        try:
            self.__foowrapper_right.is_content_respected()
        except:
            raise AssertionError('Should not raise exception')

        self.assertRaises(WopMarsParsingException, self.__foowrapper_wrong1.is_content_respected)
        self.assertRaises(WopMarsParsingException, self.__foowrapper_wrong2.is_content_respected)
        self.assertRaises(WopMarsParsingException, self.__foowrapper_wrong3.is_content_respected)
        self.assertRaises(WopMarsParsingException, self.__foowrapper_wrong4.is_content_respected)
        self.assertRaises(WopMarsParsingException, self.__foowrapper_wrong5.is_content_respected)

    def test_follows(self):
        self.assertTrue(self.__toolwrapper_second.follows(self.__toolwrapper_first))
        self.assertFalse(self.__toolwrapper_first.follows(self.__toolwrapper_second))

if __name__ == '__main__':
    unittest.main()
