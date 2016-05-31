import unittest
from unittest import TestCase

from fr.tagc.wopmars.framework.management.DAG import DAG
from fr.tagc.wopmars.framework.rule.IOFilePut import IOFilePut
from fr.tagc.wopmars.framework.rule.ToolWrapper import ToolWrapper
from fr.tagc.wopmars.utils.OptionManager import OptionManager


class TestDAG(TestCase):

    def setUp(self):
        OptionManager({'-v': 3, "--dot": None})
        #        first
        #       /    \
        #   second   third
        #       \    /
        #       fourth
        #
        self.__toolwrapper_first = ToolWrapper({"input1": IOFilePut("input1", "file1.txt")},
                                        {"output1": IOFilePut("output1", "file2.txt")},
                                        {})

        self.__toolwrapper_second = ToolWrapper({"input1": IOFilePut("input1", "file2.txt")},
                                         {"output1": IOFilePut("output1", "file3.txt")},
                                         {})

        self.__toolwrapper_third = ToolWrapper({"input1": IOFilePut("input1", "file2.txt")},
                                               {"output1": IOFilePut("output1", "file4.txt")},
                                               {})

        self.__toolwrapper_fourth = ToolWrapper({"input1": IOFilePut("input1", "file3.txt"),
                                                 "input2": IOFilePut("input2", "file4.txt")},
                                                {"output1": IOFilePut("output1", "file5.txt")},
                                                {})

        list_tool = [self.__toolwrapper_first,
                     self.__toolwrapper_second,
                     self.__toolwrapper_third,
                     self.__toolwrapper_fourth]

        self.__set_tool = set(list_tool)

    def test_init(self):
        try:
            # verifying that the dag
            my_dag = DAG(self.__set_tool)

            # Verifying that the nodes are correctly sorted
            self.assertTrue(self.__toolwrapper_fourth in my_dag.successors(self.__toolwrapper_third))
            self.assertTrue(self.__toolwrapper_fourth in my_dag.successors(self.__toolwrapper_second))
            self.assertTrue(self.__toolwrapper_second in my_dag.successors(self.__toolwrapper_first))
            self.assertTrue(self.__toolwrapper_third in my_dag.successors(self.__toolwrapper_first))
        except:
            # beware, if a test inside the try block fails, 2 exceptions are raised
            raise AssertionError('Should not raise exception')

if __name__ == '__main__':
    unittest.main()

