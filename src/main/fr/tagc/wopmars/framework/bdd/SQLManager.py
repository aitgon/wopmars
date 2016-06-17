"""
Module containing the SQLManager class.
"""
from sqlalchemy.orm import sessionmaker, scoped_session

from src.main.fr.tagc.wopmars.framework.bdd.Base import Base, Engine
from src.main.fr.tagc.wopmars.framework.bdd.WopMarsSession import WopMarsSession
from src.main.fr.tagc.wopmars.utils.Logger import Logger
from src.main.fr.tagc.wopmars.utils.RWLock import RWLock
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
        # s_database_name = "/home/giffon/db.sqlite"
        # self.__engine = create_engine('sqlite:///' + s_database_name, echo=False)
        self.__Session = scoped_session(sessionmaker(bind=Engine, autoflush=True, autocommit=False))
        self.__dict_thread_session = {}
        self.__dict_session_condition = {}
        self.__lock = RWLock()
        self.__available = True


        # Base.metadata.create_all(Engine)

    def get_session(self):
        session = WopMarsSession(self.__Session(), self)
        return session

    def commit(self, session):
        Logger.instance().debug(str(session) + " want the write lock on SQLManager.")
        self.__lock.acquire_write()
        Logger.instance().debug(str(session) + " has taken the write lock on SQLManager.")
        session.commit()
        Logger.instance().debug(str(session) + " has been commited.")
        self.__lock.release()

    def query(self, session, call):
        # todo twthread gérer le lock pour les lectures
        Logger.instance().debug(str(session) + " want the read lock on SQLManager.")
        self.__lock.acquire_read()
        Logger.instance().debug(str(session) + " has taken the read lock on SQLManager.")
        result = eval("session." + call)
        self.__lock.release()
        return result

    @staticmethod
    def drop_all():
        Base.metadata.drop_all()

    @staticmethod
    def create_all():
        # This line will create all tables found in PYTHONPATH (I think, or something like that)
        Base.metadata.create_all()