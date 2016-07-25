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
    tablename = Column(String, ForeignKey("wom_modification_table.table_name"))
    model = Column(String)
    rule_id = Column(Integer, ForeignKey("wom_rule.id"))
    type_id = Column(Integer, ForeignKey("wom_type.id"))
    used_at = Column(DateTime, nullable=True)

    # One table is in one rule
    rule = relationship("ToolWrapper", back_populates="tables", enable_typechecks=False)
    # One file has One type
    type = relationship("Type", back_populates="tables")

    modification = relationship("ModificationTable", back_populates="tables")

    tablemodelnames = set()
    tablenames = set()

    def __init__(self, model, tablename):
        """
        :param table: Base: an object extending the Base type from SQLAlchemy
        which has been created by a tool developper
        :return:
        """
        # The file containing the table should be in PYTHONPATH
        Base.__init__(self, model=model, tablename=tablename)
        Logger.instance().debug(str(model) + " model loaded. Tablename: " + str(tablename))
        self.__table = None

    @reconstructor
    def init_on_load(self):
        for table in IODbPut.tablemodelnames:
            mod = importlib.import_module(table)
            try:
                if table == self.model:
                    # todo tabling
                    self.__table = eval("mod." + self.model.split(".")[-1])
            except AttributeError as e:
                raise e
        Logger.instance().debug(self.tablename + " table class reloaded. Model: " + self.model)

    @staticmethod
    def set_tables_properties(tables):
        """
        Import the models of the current execution and then associate models with IODbPut objects.

        :param tables: Resulset IODbPut objects
        """
        # import models for avoid references errors between models when dealing with them
        IODbPut.import_models([t.model for t in tables])

        for table in tables:
            # keep track of the models used in static variable of IODbPut
            IODbPut.tablemodelnames.add(table.model)
            # Associate model with the IODbPut object
            mod = importlib.import_module(table.model)
            table_model = eval("mod." + table.model.split(".")[-1])
            table.set_table(table_model)
            # keep track of table names used in static variable of IODbPut
            IODbPut.tablenames.add(table_model.__tablename__)
            SQLManager.instance().get_session().add(table)

    @staticmethod
    def get_execution_tables():
        """
        Return all the IODbPut objects found in model IODbPut.

        :return: ResultSet IODbPut objects
        """
        session = SQLManager.instance().get_session()
        return session.query(IODbPut).all()

    @staticmethod
    def import_models(table_names):
        """
        Import all the given models

        :param table_names: Iterable containing strings of path to the models
        """
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
        if self.model != other.model or self.tablename != other.tablename:
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
                Logger.instance().debug("The table " + self.tablename + " is empty.")
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
        return "<Table (" + self.type.name + "  ):\"" + str(self.tablename) + "\"; used_at:" + str(self.used_at) + ">"

    def __str__(self):
        return "table: " + self.tablename + "; model: " + self.model