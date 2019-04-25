import importlib
import datetime
import time

from sqlalchemy.exc import OperationalError
from sqlalchemy.sql.ddl import DDL

from wopmars.framework.database.Base import Base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship, reconstructor

from wopmars.framework.database.SQLManager import SQLManager
from wopmars.framework.database.tables.IOPut import IOPut
from wopmars.framework.database.tables.ModificationTable import ModificationTable
from wopmars.framework.database.tables.ToolWrapper import ToolWrapper
from wopmars.utils.Logger import Logger
from wopmars.framework.database.tables.Type import Type
from sqlalchemy.sql.functions import func

class IODbPut(IOPut, Base):
    """
    This class extends IOPut and is specific to the input or output tables. It is the model which store the references
    to the actual tables needed by the user. The table ``wom_table`` associated with this model contains the
    following fields:

    - id: INTEGER - primary key - autoincrement - arbitrary ID
    - tablename: VARCHAR(255) - foreign key to the associated table: :class:`wopmars.framework.database.tables.ModificationTable.ModificationTable` - the name of the referenced table
    - model: VARCHAR(255) - the path to the model (in python notation)
    - rule_id: INTEGER - foreign key to the associated rule ID: :class:`wopmars.framework.database.tables.ToolWrapper.ToolWrapper`
    - type_id: INTEGER - foreign key to the associated type ID: :class:`wopmars.framework.database.tables.Type.Type`
    - used_at: DATE - date at which the table have been used
    """
    __tablename__ = "wom_table"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tablename = Column(String(255), ForeignKey("wom_modification_table.table_name"))
    model = Column(String(255))
    rule_id = Column(Integer, ForeignKey("wom_rule.id"))
    type_id = Column(Integer, ForeignKey("wom_type.id"))
    used_at = Column(DateTime, nullable=True)

    # One table is in one rule
    rule = relationship("ToolWrapper", back_populates="tables", enable_typechecks=False)
    # One file has One type
    type = relationship("Type", back_populates="tables")

    modification = relationship("ModificationTable", back_populates="tables")

    # all the model names met since the begining of this instance of WopMaRS
    tablemodelnames = set()
    # al the table names met since the begining of this instance of WopMaRS
    tablenames = set()

    def __init__(self, model, tablename):
        """
        self.__table is initialized to None and will contain the model of this IODbPut object.

        :param model: The path to the model
        :type model: str
        :param tablename: The name of the table associated with the model
        :type tablename: str
        """
        # The file containing the table should be in PYTHONPATH
        Base.__init__(self, model=model, tablename=tablename)
        Logger.instance().debug(str(model) + " model loaded. Tablename: " + str(tablename))
        self.__table = None

    @reconstructor
    def init_on_load(self):
        """
        This is used by SQLAlchemy to regenerate the right object when loading it from the database. Here, we need to
        get back the actual Model from the model name and store it in self.__table.
        """
        for table in IODbPut.tablemodelnames:
            mod = importlib.import_module(table)
            try:
                if table == self.model:
                    # todo tabling
                    self.__table = eval("mod." + self.model.split(".")[-1])
            except AttributeError as e:
                raise e
        Logger.instance().debug(self.tablename + " table class reloaded. Model: " + self.model)

    def set_table(self, model):
        self.__table = model

    def get_table(self):
        return self.__table

    @staticmethod
    def create_triggers():
        """
        Create an INSERT, UPDATE, DELETE trigger on the tables created by the user in order to store the modifications date.
        """
        stmt = ["INSERT", "UPDATE", "DELETE"]
        for tablename in Base.metadata.tables:
            if tablename[:4] != "wom_":
                for s in stmt:
                    data={"statement": str(s), "tablename": str(tablename)} 
                    if SQLManager.instance().__dict__['d_database_config']['db_connection'] == 'sqlite':
                        sql_trigger = """CREATE TRIGGER IF NOT EXISTS trigger_modif_%(tablename)s_%(statement)s AFTER %(statement)s ON %(tablename)s BEGIN UPDATE wom_modification_table SET date = CURRENT_TIMESTAMP WHERE table_name = '%(tablename)s'; END;"""%data
                    elif SQLManager.instance().__dict__['d_database_config']['db_connection'] == 'mysql':
                        sql_trigger = """
CREATE TRIGGER IF NOT EXISTS modification_%(tablename)s_%(statement)s AFTER %(statement)s ON %(tablename)s for each row UPDATE wom_modification_table SET date = CURRENT_TIMESTAMP WHERE table_name = '%(tablename)s';
    """%data
                        obj_ddl = DDL(sql_trigger)
                        SQLManager.instance().create_trigger(Base.metadata.tables[tablename], obj_ddl)
                    elif SQLManager.instance().__dict__['d_database_config']['db_connection'] == 'postgresql':
                        sql_trigger = """
CREATE OR REPLACE FUNCTION modification_%(statement)s_%(tablename)s() RETURNS TRIGGER AS $modification_%(statement)s_%(tablename)s$
BEGIN
UPDATE wom_modification_table SET date = CURRENT_TIMESTAMP WHERE table_name = '%(tablename)s';
RETURN NULL; -- result is ignored since this is an AFTER trigger
END;
$modification_%(statement)s_%(tablename)s$ LANGUAGE plpgsql;
DROP TRIGGER IF EXISTS modification_%(statement)s_%(tablename)s ON "%(tablename)s";
CREATE TRIGGER modification_%(statement)s_%(tablename)s AFTER INSERT ON "%(tablename)s" FOR EACH ROW EXECUTE PROCEDURE modification_%(statement)s_%(tablename)s();
    """%data
                    # import pdb; pdb.set_trace()
                    obj_ddl = DDL(sql_trigger)
                    SQLManager.instance().create_trigger(Base.metadata.tables[tablename], obj_ddl)


    @staticmethod
    def set_tables_properties(tables):
        """
        Import the models of the current execution and then associate models with IODbPut objects.

        :param tables: the IODbPut which need their table properties to be set.
        :type tables: ResultSet(IODbPut)
        """
        # import models for avoid references errors between models when dealing with them
        IODbPut.import_models(set([t.model for t in tables]))

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
        execution_id = session.query(func.max(ToolWrapper.execution_id))
        return session.query(IODbPut).filter(IODbPut.rule_id == ToolWrapper.id).filter(ToolWrapper.execution_id == execution_id).all()

    @staticmethod
    def import_models(model_names):
        """
        Import all the given models

        :param model_names: The path to the models
        :type model_names: Iterable(String)
        """
        for t in model_names:
            Logger.instance().debug("IODbPut.import_models: importing " + str(t))
            importlib.import_module(t)

    def is_ready(self):
        """
        A IODbPut object is ready if its table exists and contains entries.

        :return: bool if the table is ready
        """
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
            # todo twthread
        return True

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
            raise e
        return True

    def __hash__(self):
        return id(self)

    def __repr__(self):
        return "<Table (" + self.type.name + "  ):\"" + str(self.tablename) + "\"; used_at:" + str(self.used_at) + ">"

    def __str__(self):
        return "<Table: " + self.tablename + "; model: " + self.model + ">"
