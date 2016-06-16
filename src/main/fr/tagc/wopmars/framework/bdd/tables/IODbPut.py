"""
Module containing the IODbPut class.
"""
import importlib

from src.main.fr.tagc.wopmars.framework.bdd.Base import Base, Engine
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, reconstructor

from src.main.fr.tagc.wopmars.framework.bdd.SQLManager import SQLManager
from src.main.fr.tagc.wopmars.framework.bdd.tables.IOPut import IOPut
from src.main.fr.tagc.wopmars.utils.Logger import Logger

# todo retourner nom de la table
class IODbPut(IOPut, Base):
    """
    This class extends IOPut and is specific to table input or output
    """
    __tablename__ = "table"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    rule_id = Column(Integer, ForeignKey("rule.id"))
    type_id = Column(Integer, ForeignKey("type.id"))

    # One table is in one rule
    rule = relationship("ToolWrapper", back_populates="tables", enable_typechecks=False)
    # One file has One type
    type = relationship("Type", back_populates="tables")

    def __init__(self, name):
        """
        :param table: Base: an object extending the Base type from SQLAlchemy
        which has been created by a tool developper
        :return:
        """
        # The file containing the table should be in PYTHONPATH
        Base.__init__(self, name=name)
        mod = importlib.import_module(name)
        self.__table = eval("mod." + name)
        Base.metadata.tables[self.__table.__tablename__].create(Engine, checkfirst=True)
        Logger.instance().debug(name + " table class loaded.")

    @reconstructor
    def init_on_load(self):
        mod = importlib.import_module(self.name)
        self.__table = eval("mod." + self.name)
        # todo ask lionel les tables spécifiques des classes métiers ne sont pas crées au tout début....
        # je ne sais pas pourquoi mais c'est arrangeant
        Base.metadata.tables[self.__table.__tablename__].create(Engine, checkfirst=True)

    def get_table(self):
        return self.__table

    def __eq__(self, other):
        """
        Two IODbPut object are equals if their table attributes belongs to the same class and if the associated table
        has the same content

        :param other: IODbPut
        :return: boolean: True if the table attributes are the same, False if not
        """
        session = SQLManager.instance().get_session()
        if self.name != other.name:
            return False
        try:
            self_results = set(session.query(self.__table).all())
            other_results = set(session.query(other.get_table()).all())
            if self_results != other_results:
                return False
        except Exception as e:
            session.rollback()
            # session.close()
            raise e
        return True

    def is_ready(self):
        session = SQLManager.instance().get_session()
        try:
            results = session.query(self.__table).first()
            if results is None:
                Logger.instance().info("The table " + self.name + " is empty.")
                return False
        except Exception as e:
            session.rollback()
            raise e
        # finally:
            # todo twthread
            # session.close()
        return True

    def __hash__(self):
        return id(self)

    def __repr__(self):
        return "<Table:\"" + str(self.name) + "\">"

