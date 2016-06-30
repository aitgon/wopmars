"""
Module containing the SQLManager class.
"""
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine

from src.main.fr.tagc.wopmars.framework.bdd.Base import Base
from src.main.fr.tagc.wopmars.framework.bdd.WopMarsSession import WopMarsSession
from src.main.fr.tagc.wopmars.utils.Logger import Logger
from src.main.fr.tagc.wopmars.utils.OptionManager import OptionManager
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
        #  = create_engine('sqlite:///' + s_database_name, echo=False)
        s_database_name = OptionManager.instance()["DATABASE"]

        self.__engine = create_engine('sqlite:///' + s_database_name, echo=False)
        self.__Session = scoped_session(sessionmaker(bind=self.__engine, autoflush=True, autocommit=False))
        self.__dict_thread_session = {}
        self.__dict_session_condition = {}
        self.__lock = RWLock()
        self.__available = True


        # Base.metadata.create_all(Engine)

    def get_engine(self):
        return self.__engine

    def get_session(self):
        session = WopMarsSession(self.__Session(), self)
        return session

    def commit(self, session):
        """
        The SQLManager wrap the sqlite queue for operations on database in order to do not trigger the execution due
        to the time-out operations.

        This is done thanks to a read_write_lock: sqlmanager is a synchronized singleton with a synchronized method

        :param session: sqlalchemy session
        :return:
        """
        try:
            Logger.instance().debug(str(session) + " want the write lock on SQLManager.")
            self.__lock.acquire_write()
            # todo faire peut etre try catch de la session ici
            Logger.instance().debug(str(session) + " has taken the write lock on SQLManager.")
            session.commit()
            Logger.instance().debug(str(session) + " has been commited.")
        finally:
            self.__lock.release()
            Logger.instance().debug(str(session) + " has released the write lock on SQLManager.")

    # def query(self, session, call):
    #     # todo twthread gérer le lock pour les lectures
    #     # -> recuperer l'objet query et faire le call ici (all, one, first... )
    #     # todo ask lionel, comment tu ferais? faire le eval
    #     Logger.instance().debug(str(session) + " want the read lock on SQLManager.")
    #     self.__lock.acquire_read()
    #     Logger.instance().debug(str(session) + " has taken the read lock on SQLManager.")
    #     result = eval("session." + call)
    #     self.__lock.release()
    #     return result

    def execute(self, session, statement):
        try:
            Logger.instance().debug(str(session) + " want the write lock on SQLManager for statement \"" + str(statement) + "\"")
            self.__lock.acquire_write()
            Logger.instance().debug(str(session) + " has taken the write lock on SQLManager.")
            session.execute(statement)
        finally:
            self.__lock.release()
            Logger.instance().debug(str(session) + " has released the write lock on SQLManager.")

    def rollback(self, session):
        try:
            Logger.instance().debug(str(session) + " want the write lock on SQLManager.")
            self.__lock.acquire_write()
            # todo faire peut etre try catch de la session ici
            Logger.instance().debug(str(session) + " has taken the write lock on SQLManager.")
            session.rollback()
            Logger.instance().debug(str(session) + " has been rollbacked.")
        finally:
            self.__lock.release()
            Logger.instance().debug(str(session) + " has released the write lock on SQLManager.")

    @staticmethod
    def drop_all():
        """
        Use the declarative Base to drop all tables found. Should only be used for testing purposes.
        :return:
        """
        Base.metadata.drop_all(SQLManager.instance().get_engine())
        # todo ask aitor option pour reset les resultats (supprimer le contenu de la bdd) / fresh run
        # (suppression de la bdd avant run pour etre sur de repartir sur des bases saines)

    @staticmethod
    def create_all():
        """
        Use the declarative Base to create all tables found (especially whose which are related to the workflow management).

        :return: void
        """
        # This line will create all tables found in PYTHONPATH (I think, or something like that)
        Base.metadata.create_all(SQLManager.instance().get_engine())

    def create(self, tablename):
        try:
            self.__lock.acquire_write()
            Base.metadata.tables[tablename].create(self.__engine, checkfirst=True)
        finally:
            self.__lock.release()

    def drop(self, tablename):
        try:
            self.__lock.acquire_write()
            Base.metadata.tables[tablename].drop(self.__engine, checkfirst=True)
        finally:
            self.__lock.release()