"""
Module containing the IODbPut class.
"""
from src.main.fr.tagc.wopmars.framework.bdd.Base import Base
from src.main.fr.tagc.wopmars.framework.bdd.SQLManager import SQLManager
from src.main.fr.tagc.wopmars.framework.rule.IOPut import IOPut

import collections


class IODbPut(IOPut):
    """
    This class extends IOPut and is specific to table input or output
    """    
    def __init__(self, table):
        """
        :param table: Base: an object extending the Base type from SQLAlchemy
        which has been created by a tool developper
        :return:
        """
        assert issubclass(table, Base)
        self.__table = table
        super().__init__(self.__table.__class__.__name__)

    def get_table(self):
        """
        Return the Base object contained.

        :return: Base: the SQL alchemy object corresponding to the table
        """
        return self.__table

    def __eq__(self, other):
        """
        Two IODbPut object are equals if their table attributes belongs to the same class and if the associated table
        has the same content

        :param other: IODbPut
        :return: boolean: True if the table attributes are the same, False if not
        """
        # TODO method __eq__ doit aussi vérifier le contenu des tables
        session = SQLManager.instance().get_session()
        if self.__table != other.get_table():
            return False
        try:
            self_results = set(session.query(self.__table).all())
            other_results = set(session.query(other.get_table()).all())
            if self_results != other_results:
                return False


        except Exception as e:
            session.rollback()
            session.close()
            raise e
        return True

    def is_ready(self):
        session = SQLManager.instance().get_session()
        try:
            results = session.query(self.__table).first()
            if results is None:
                return False
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
        return True

    def __hash__(self):
        return id(self)

    def __repr__(self):
        return "table:\"" + self.__table + "\""

