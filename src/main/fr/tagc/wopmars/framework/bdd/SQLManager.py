"""
Module containing the SQLManager class.
"""
import threading
from queue import Queue

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from src.main.fr.tagc.wopmars.framework.bdd.WopMarsSession import WopMarsSession
from src.main.fr.tagc.wopmars.utils.OptionManager import OptionManager
from src.main.fr.tagc.wopmars.utils.Singleton import SingletonMixin


class SQLManager(SingletonMixin):
    """
    class SQLManager
    """

    def __init__(self):
        """
        

        :return:
        """
        # todo optionmanager
        s_database_name = "/home/giffon/db.sqlite"
        self.__engine = create_engine('sqlite:///' + s_database_name, echo=False)
        self.__Session = scoped_session(sessionmaker(bind=self.__engine, autoflush=True, autocommit=False))
        self.__dict_thread_session = {}
        self.__dict_session_condition = {}
        self.__queue_commit = Queue()
        self.__cv_current_commit = threading.Condition()
        self.__available = True

    def get_session(self):
        session = WopMarsSession(self.__Session(), self)
        return session

    def get_engine(self):
        return self.__engine

    def commit(self, session):
        with self.__cv_current_commit:
            while not self.__available:
                self.__cv_current_commit.wait()
            self.__available = False
            session.commit()
            self.__available = True
            self.__cv_current_commit.notify()
