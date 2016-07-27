"""
Module containing the IODbPut class.
"""
import importlib
import datetime
import time

from sqlalchemy.exc import OperationalError

from src.main.fr.tagc.wopmars.framework.bdd.Base import Base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship, reconstructor

from src.main.fr.tagc.wopmars.framework.bdd.SQLManager import SQLManager
from src.main.fr.tagc.wopmars.framework.bdd.tables.IOPut import IOPut
from src.main.fr.tagc.wopmars.framework.bdd.tables.ModificationTable import ModificationTable
from src.main.fr.tagc.wopmars.utils.Logger import Logger
from src.main.fr.tagc.wopmars.framework.bdd.tables.Type import Type


class IODbPut(IOPut, Base):
    """
    This class extends IOPut and is specific to table input or output
    """
    __tablename__ = "wom_table"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, ForeignKey("wom_modification_table.table_name"))
    rule_id = Column(Integer, ForeignKey("wom_rule.id"))
    type_id = Column(Integer, ForeignKey("wom_type.id"))
    used_at = Column(DateTime, nullable=True)

    # One table is in one rule
    rule = relationship("ToolWrapper", back_populates="tables", enable_typechecks=False)
    # One file has One type
    type = relationship("Type", back_populates="tables")

    modification = relationship("ModificationTable", back_populates="tables")

    tables = set()
    tablenames = set()

    def __init__(self, name):
        """
        :param table: Base: an object extending the Base type from SQLAlchemy
        which has been created by a tool developper
        :return:
        """
        # The file containing the table should be in PYTHONPATH
        Base.__init__(self, name=name)
        Logger.instance().debug(name + " table class loaded.")
        self.__table = None

    @reconstructor
    def init_on_load(self):
        for table in IODbPut.tables:
            mod = importlib.import_module(table)
            try:
                if table == self.name:
                    # todo tabling
                    self.__table = eval("mod." + self.name.split(".")[-1])
            except AttributeError as e:
                raise e
        Logger.instance().debug(self.name + " table class reloaded.")


    @staticmethod
    def set_tables_properties(tables):
        IODbPut.import_models([t.name for t in tables])

        for table in tables:
            IODbPut.tables.add(table.name)
            mod = importlib.import_module(table.name)
            table.set_table(eval("mod." + table.name.split(".")[-1]))
            IODbPut.tablenames.add(table.get_table().__tablename__)
            SQLManager.instance().get_session().add(table)

    @staticmethod
    def get_execution_tables():
        session = SQLManager.instance().get_session()
        return session.query(IODbPut).all()

    @staticmethod
    def import_models(table_names):
        for t in table_names:
            importlib.import_module(t)

    def set_table(self, model):
        self.__table = model

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
                Logger.instance().debug("The table " + self.name + " is empty.")
                return False
        except OperationalError as e:
            Logger.instance().debug("The table " + self.__table.__tablename__ + " doesn't exist.")
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
        return "<Table (" + self.type.name + "  ):\"" + str(self.name) + "\"; used_at:" + str(self.used_at) + ">"

    def __str__(self):
        return "table: " + self.name