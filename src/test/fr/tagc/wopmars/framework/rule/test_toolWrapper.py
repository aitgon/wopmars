import os
import unittest
from unittest import TestCase

from FooWrapper8 import FooWrapper8
from FooWrapperNoTable import FooWrapperNoTable
from src.main.fr.tagc.wopmars.framework.rule.IOFilePut import IOFilePut
from src.main.fr.tagc.wopmars.framework.rule.Option import Option
from src.main.fr.tagc.wopmars.framework.rule.ToolWrapper import ToolWrapper
from src.main.fr.tagc.wopmars.utils.OptionManager import OptionManager
from src.main.fr.tagc.wopmars.utils.PathFinder import PathFinder
from src.main.fr.tagc.wopmars.utils.exceptions.WopMarsException import WopMarsException
from src.test.fr.tagc.wopmars.toolwrappers.FooWrapper3 import FooWrapper3


class TestToolWrapper(TestCase):
    def setUp(self):
        OptionManager({'-v': 1, "--dot": None})

        ### Toolwrappers for __eq__ test

        self.__toolwrapper1 = ToolWrapper({"input1": IOFilePut("input1", "file1.txt")},
                                          {"output1": IOFilePut("output1", "file2.txt")},
                                          {"param1": Option("param1", 1)})

        self.__toolwrapper2 = ToolWrapper({"input1": IOFilePut("input1", "file1.txt")},
                                          {"output1": IOFilePut("output1", "file2.txt")},
                                          {"param1": Option("param1", 1)})

        self.__toolwrapper3 = ToolWrapper({"input1": IOFilePut("input1", "file1.txt")},
                                          {"output1": IOFilePut("output1", "file2.txt")},
                                          {"param1": Option("param1", 3)})

        ### ToolWrappers for content_respected

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

        ### TooLWrappers for follows

        self.__toolwrapper_first = ToolWrapper({"input1": IOFilePut("input1", "file1.txt")},
                                               {"output1": IOFilePut("output1", "file2.txt")},
                                               {})

        self.__toolwrapper_second = ToolWrapper({"input1": IOFilePut("input1", "file2.txt")},
                                                {"output1": IOFilePut("output1", "file3.txt")},
                                                {})


        ### ToolWrappers for are_input_ready

        s_root_path = PathFinder.find_src(os.path.dirname(os.path.realpath(__file__)))

        s_path_to_example_file_that_exists = s_root_path + "resources/aFile1.txt"

        self.__toolwrapper_ready = ToolWrapper({"input1": IOFilePut("input1", s_path_to_example_file_that_exists)},
                                               {},
                                               {})

        self.__toolwrapper_not_ready = ToolWrapper({"input1": IOFilePut("input1", "/not/existent/file")},
                                               {},
                                               {})


        ### ToolWrapper for load_tables method

        self.__toolwrapper_empty = ToolWrapper()

    def test_init(self):
        try:
            FooWrapper8({}, {}, {})
        except:
            AssertionError("Should not raise an exception.")

        with self.assertRaises(WopMarsException):
            FooWrapperNoTable()

    def test_load_tables(self):
        try:
            self.__toolwrapper_empty.load_tables(["FooBase"], 'input')
            self.__toolwrapper_empty.load_tables(["FooBase"], 'output')
            self.__toolwrapper_empty.load_tables(["FooBase"], 'fail')
        except:
            AssertionError('Should not raise an exception.')

        with self.assertRaises(WopMarsException):
            self.__toolwrapper_empty.load_tables(["Failure"], 'input')

        with self.assertRaises(WopMarsException):
            self.__toolwrapper_empty.load_tables(["BaseWrongClassName"], 'input')

        with self.assertRaises(WopMarsException):
            self.__toolwrapper_empty.load_tables(["Failure"], 'input')

    def test_eq(self):
        self.assertEqual(self.__toolwrapper1, self.__toolwrapper2)
        self.assertNotEqual(self.__toolwrapper1, self.__toolwrapper3)

    def test_is_content_respected(self):
        try:
            self.__foowrapper_right.is_content_respected()
        except:
            raise AssertionError('Should not raise exception')

        self.assertRaises(WopMarsException, self.__foowrapper_wrong1.is_content_respected)
        self.assertRaises(WopMarsException, self.__foowrapper_wrong2.is_content_respected)
        self.assertRaises(WopMarsException, self.__foowrapper_wrong3.is_content_respected)
        self.assertRaises(WopMarsException, self.__foowrapper_wrong4.is_content_respected)
        self.assertRaises(WopMarsException, self.__foowrapper_wrong5.is_content_respected)

    def test_follows(self):
        self.assertTrue(self.__toolwrapper_second.follows(self.__toolwrapper_first))
        self.assertFalse(self.__toolwrapper_first.follows(self.__toolwrapper_second))

    def test_are_inputs_ready(self):
        self.assertTrue(self.__toolwrapper_ready.are_inputs_ready())
        self.assertFalse(self.__toolwrapper_not_ready.are_inputs_ready())

if __name__ == '__main__':
    unittest.main()
