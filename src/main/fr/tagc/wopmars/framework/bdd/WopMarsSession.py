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
        # Logger.instance().debug(str(self.__session) + " is about to commit.")
        Logger.instance().debug("Operations to be commited in session" + str(self.__session) + ": \n\tUpdates:\n\t\t" +
                                "\n\t\t".join([str(k) for k in self.__session.dirty]) +
                                "\n\tInserts:\n\t\t" +
                                "\n\t\t".join([str(k) for k in self.__session.new]))
        self.__manager.commit(self.__session)

    def rollback(self):
        Logger.instance().debug("Operations to be commited in session" + str(self.__session) + ": \n\tUpdates:\n\t\t" +
                                "\n\t\t".join([str(k) for k in self.__session.dirty]) +
                                "\n\tInserts:\n\t\t" +
                                "\n\t\t".join([str(k) for k in self.__session.new]))
        self.__session.rollback()

    def query(self, table):
        return self.__session.query(table)

    def add(self, item):
        """
        Add
        :param item:
        :return:
        """
        self.__session.add(item)

    def delete(self, entry):
        self.__session.delete(entry)

    def close(self):
        self.__session.close()

    def _session(self):
        return self.__session
