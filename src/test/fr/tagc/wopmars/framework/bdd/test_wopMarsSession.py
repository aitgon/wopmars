import unittest
from unittest import TestCase

from FooBase import FooBase
from src.main.fr.tagc.wopmars.framework.bdd.SQLManager import SQLManager
from src.main.fr.tagc.wopmars.utils.OptionManager import OptionManager
from src.main.fr.tagc.wopmars.utils.PathFinder import PathFinder


class TestWopMarsSession(TestCase):
    def setUp(self):
        OptionManager.initial_test_setup()
        SQLManager.instance().create_all()
        self.__session = SQLManager.instance().get_session()

    def tearDown(self):
        self.__session.rollback()
        SQLManager.drop_all()
        PathFinder.dir_content_remove("resources/outputs/")
        OptionManager._drop()
        SQLManager._drop()

    def test_commit_query_add(self):
        for i in range(10):
            f = FooBase(name="testSession " + str(i))
            self.__session.add(f)
        self.__session.commit()
        self.assertEqual(len(self.__session.query(FooBase).all()), 10)

    def test_rollback(self):
        for i in range(10):
            f = FooBase(name="testSession " + str(i))
            self.__session.add(f)
        self.__session.rollback()
        self.assertEqual(len(self.__session.query(FooBase).all()), 0)

    def test_add_all(self):
        fs = []
        for i in range(10):
            fs.append(FooBase(name="testSession " + str(i)))
        self.__session.add_all(fs)
        self.__session.commit()
        self.assertEqual(len(self.__session.query(FooBase).all()), 10)

    def test_delete(self):
        fs = []
        for i in range(10):
            fs.append(FooBase(name="testSession " + str(i)))
        self.__session.add_all(fs)
        self.__session.commit()

        for i in range(5):
            f = self.__session.query(FooBase).filter(FooBase.name == "testSession " + str(i)).first()
            self.__session.delete(f)
        self.assertEqual(len(self.__session.query(FooBase).all()), 5)

    def test_delete_content(self):
        fs = []
        for i in range(10):
            fs.append(FooBase(name="testSession " + str(i)))
        self.__session.add_all(fs)
        self.__session.commit()

        self.__session.delete_content(FooBase)
        self.assertEqual(len(self.__session.query(FooBase).all()), 0)

    def test_something(self):
        fs = []
        for i in range(10):
            fs.append(FooBase(name="testSession " + str(i)))
        self.__session.add_all(fs)
        self.assertTrue(self.__session.something())

        self.__session.commit()
        self.assertFalse(self.__session.something())

        for i in range(10):
            self.__session.query(FooBase).filter(FooBase.name == "testSession " + str(i)).first().name = "sessionTest " + str(i)
        self.assertTrue(self.__session.something())

    def test_get_or_create(self):
        fs = []
        for i in range(10):
            fs.append(FooBase(name="testSession " + str(i)))
        self.__session.add_all(fs)
        self.__session.commit()
        self.assertEqual(self.__session.get_or_create(FooBase, name="testSession 0")[0], fs[0])
        self.__session.delete(fs[0])
        self.assertNotEqual(self.__session.get_or_create(FooBase, name="testSession 0")[0], fs[0])

if __name__ == '__main__':
    unittest.main()