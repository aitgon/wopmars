"""
Module containing the WopMarsSession class.
"""
from sqlalchemy.sql.elements import ClauseElement

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
        if self.something():
            Logger.instance().debug(str(self.__session) + " is about to commit.")
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

    def add_all(self, collection):
        self.__session.add_all(collection)

    def delete(self, entry):
        self.__session.delete(entry)

    def delete_content(self, table):
        for e in self.__session.query(table).all():
            self.__session.delete(e)

    def close(self):
        self.__session.close()

    def _session(self):
        return self.__session

    def something(self):
        return bool(self.__session.new) or bool(self.__session.dirty)

    def get_or_create(self, model, defaults=None, **kwargs):
        instance = self.__session.query(model).filter_by(**kwargs).first()
        if instance:
            return instance, False
        else:
            params = dict((k, v) for k, v in kwargs.items() if not isinstance(v, ClauseElement))
            params.update(defaults or {})
            instance = model(**params)
            self.__session.add(instance)
            return instance, True
