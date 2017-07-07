import threading
import unittest
from unittest import TestCase

from test.resource.model.FooBase import FooBase
from wopmars.framework.database.SQLManager import SQLManager
from wopmars.utils.OptionManager import OptionManager


class ConcurrentCommitingThread(threading.Thread):
    def run(self):
        thread_session = SQLManager.instance().get_session()
        for i in range(1000):
            foo = FooBase(name="string " + str(i))
            thread_session.add(foo)
        thread_session.commit()

        thread_session.close()


# todo LG: refaire test_bak rollback
class ConcurrentRollBackingThread(threading.Thread):
    def run(self):
        thread_session = SQLManager.instance().get_session()
        for i in range(1000):
            foo = FooBase(name="string " + str(i))
            thread_session.add(foo)
        thread_session.rollback()

        thread_session.close()


class TestSQLManager(TestCase):
    def setUp(self):
        OptionManager.initial_test_setup()
        SQLManager.instance().create_all()
        self.__local_session = SQLManager.instance().get_session()

        SQLManager()
        self.__t1 = ConcurrentCommitingThread()
        self.__t2 = ConcurrentCommitingThread()
        self.__t3 = ConcurrentCommitingThread()

        self.__t4 = ConcurrentRollBackingThread()
        self.__t5 = ConcurrentRollBackingThread()
        self.__t6 = ConcurrentRollBackingThread()

    def test_commit(self):
        list_threads = [self.__t1, self.__t2, self.__t3, self.__t4, self.__t5, self.__t6]
        try:
            for t in list_threads:
                t.start()

            for t in list_threads:
                t.join()
        except Exception as e:
            print(e)
            raise AssertionError("Should not raise an exception")

        self.assertTrue(len(self.__local_session.query(FooBase).filter(FooBase.name.like('string %')).all()) == 3000)

    def tearDown(self):
        SQLManager.instance().get_session().close()
        SQLManager.instance().drop_all()
        OptionManager._drop()
        SQLManager._drop()

if __name__ == '__main__':
    unittest.main()
