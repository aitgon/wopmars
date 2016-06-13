import queue
import unittest
from unittest import TestCase

from src.main.fr.tagc.wopmars.utils.UniqueQueue import UniqueQueue


class TestUniqueQueue(TestCase):
    def setUp(self):
        self.__queue = UniqueQueue()
        self.__queue.put(1)
        self.__queue.put(2)
        self.__queue.put(1)


    def test__put(self):
        try:
            self.__queue.get_nowait()
            self.__queue.get_nowait()
        except:
            AssertionError("Should not raise an exception")

        self.assertRaises(queue.Empty, self.__queue.get_nowait)

if __name__ == '__main__':
    unittest.main()