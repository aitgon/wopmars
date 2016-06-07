"""
Module containing the WopMarsSession class.
"""
from src.main.fr.tagc.wopmars.utils.Logger import Logger


class WopMarsSession:
    """
    class WopMarsSession
    """

    def __init__(self, session, manager):
        """
        

        :return:
        """
        self.__manager = manager
        self.__session = session

    def commit(self):
        Logger().debug("Operations to be commited: \n\tUpdates:\n\t\t" +
                       "\n\t\t".join([str(k) for k in self.__session.dirty]) +
                       "\n\tInserts:\n\t\t" +
                       "\n\t\t".join([str(k) for k in self.__session.new]))
        self.__manager.commit(self.__session)

    def rollback(self):
        pass

    def query(self):
        pass

    def add(self, item):
        """
        Add
        :param item:
        :return:
        """
        self.__session.add(item)

    def delete(self):
        pass