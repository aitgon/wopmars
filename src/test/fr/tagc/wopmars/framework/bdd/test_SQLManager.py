from unittest import TestCase
import unittest
import threading

from FooBase import FooBase
from src.main.fr.tagc.wopmars.framework.bdd.SQLManager import SQLManager
from src.main.fr.tagc.wopmars.utils.OptionManager import OptionManager


class ConcurrentCommitingThread(threading.Thread):
    def run(self):
        thread_session = SQLManager.instance().get_session()
        for i in range(1000):
            foo = FooBase(name="string " + str(i))
            thread_session.add(foo)
        thread_session.commit()

        thread_session.close()


class TestSQLManager(TestCase):
    def setUp(self):
        OptionManager({'-v':4})
        SQLManager()
        self.__t1 = ConcurrentCommitingThread()
        self.__t2 = ConcurrentCommitingThread()
        self.__t3 = ConcurrentCommitingThread()

    def test_commit(self):
        list_threads = [self.__t1, self.__t2, self.__t3]
        try:
            for t in list_threads:
                t.start()

            for t in list_threads:
                t.join()
        except Exception as e:
            print(e)
            raise AssertionError("Should not raise an exception")

    def tearDown(self):
        local_session = SQLManager().get_session()
        foo_objects = local_session.query(FooBase).filter(FooBase.name.like('string %')).all()
        for obj in foo_objects:
            local_session.delete(obj)
        local_session.commit()

if __name__ == '__main__':
    unittest.main()