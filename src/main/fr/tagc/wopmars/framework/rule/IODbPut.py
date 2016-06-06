"""
Module containing the IODbPut class.
"""
from src.main.fr.tagc.wopmars.base.Base import Base
from src.main.fr.tagc.wopmars.framework.rule.IOPut import IOPut


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
        assert isinstance(table, Base)
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
        assert isinstance(other, self.__class__)
        return isinstance(self.__table, other.get_table().__class__)

    def is_ready(self):
        # TODO faire correctement cette méthode pour qu'elle vérifie que les tables existent et sont remplies
        return False

    def __hash__(self):
        return id(self)

    def __repr__(self):
        return "table:\"" + self.__table + "\""

