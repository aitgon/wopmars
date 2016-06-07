"""
Module containing the SQLManager class.
"""
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
        s_database_name = "db.sqlite"
        engine = create_engine('sqlite:///' + s_database_name, echo=False)
        self.__Session = scoped_session(sessionmaker(bind=engine, autoflush=True, autocommit=False))
        self.__queue = Queue()

    def get_session(self):
        return WopMarsSession(self.__Session())
