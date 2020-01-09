import importlib

from sqlalchemy.exc import OperationalError

from wopmars.Base import Base
from sqlalchemy import Column, Integer, String, ForeignKey, BigInteger, Boolean, DateTime
from sqlalchemy.orm import relationship, reconstructor

from wopmars.SQLManager import SQLManager
from wopmars.models.InputOutput import InputOutput
from wopmars.models.ToolWrapper import ToolWrapper
from wopmars.utils.Logger import Logger
from sqlalchemy.sql.functions import func


class TableInputOutputInformation(InputOutput, Base):
    """
    This class extends InputOutput and is specific to the input or output tables. It is the model which store the references
    to the actual tables needed by the user. The table ``wom_table_io_information`` associated with this model contains the
    following fields:

    - id: INTEGER - primary key - autoincrement - arbitrary ID
    - tablename: VARCHAR(255) - foreign key to the associated table: :class:`wopmars.framework.database.relation_toolwrapper_to_tableioinfo.TableModificationTime.TableModificationTime` - the is_input of the referenced table
    - model: VARCHAR(255) - the path to the model (in python notation)
    - toolwrapper_id: INTEGER - foreign key to the associated rule ID: :class:`wopmars.framework.database.relation_toolwrapper_to_tableioinfo.ToolWrapper.ToolWrapper`
    - is_input: INTEGER - foreign key to the associated type ID: :class:`wopmars.framework.database.relation_toolwrapper_to_tableioinfo.TypeInputOrOutput.TypeInputOrOutput`
    - mtime_epoch_millis: INTEGER - unix mtime_epoch_millis at which the table have been used
    """

    __tablename__ = "wom_{}".format(__qualname__)

    id = Column(Integer, primary_key=True, autoincrement=True)
    table_key = Column(String(255))
    table_name = Column(String(255), ForeignKey("wom_TableModificationTime.table_name"))
    model_py_path = Column(String(255))
    toolwrapper_id = Column(Integer, ForeignKey("wom_ToolWrapper.id", ondelete='CASCADE'))
    is_input = Column(Boolean, ForeignKey("wom_TypeInputOrOutput.is_input"))
    mtime_human = Column(DateTime, nullable=True)
    mtime_epoch_millis = Column(BigInteger, nullable=True)

    # One toolwrapper uses many tables
    relation_file_or_tableioinfo_to_toolwrapper = relationship("ToolWrapper", back_populates="relation_toolwrapper_to_tableioinfo", enable_typechecks=False)
    # One type_io is used by many tables
    relation_file_or_tableioinfo_to_typeio = relationship("TypeInputOrOutput", back_populates="relation_typeio_to_tableioinfo")
    # One table_io_info has one table_modif_time
    relation_tableioinfo_to_tablemodiftime = relationship("TableModificationTime", back_populates="relation_tablemodiftime_to_tableioinfo")

    # all the model names met since the begining of this instance of WopMaRS
    tablemodelnames = set()
    # al the table names met since the begining of this instance of WopMaRS
    tablenames = set()

    def __init__(self, model_py_path, table_key, table_name):
        """
        self.__table is initialized to None and will contain the model of this TableInputOutputInformation object.

        :param model_py_path: The path to the model
        :type model_py_path: str
        :param table_key: The is_input of the table associated with the model
        :type table_key: str
        """
        # The file containing the table should be in PYTHONPATH
        Base.__init__(self, model_py_path=model_py_path, table_key=table_key, table_name=table_name)
        Logger.instance().debug(str(model_py_path) + " model_py_path loaded. Tablename: " + str(table_key))
        self.__table = None

    @reconstructor
    def init_on_load(self):
        """
        This is used by SQLAlchemy to regenerate the right object when loading it from the database. Here, we need to
        get back the actual Model from the model is_input and store it in self.__table.
        """
        for table in TableInputOutputInformation.tablemodelnames:
            mod = importlib.import_module(table)
            try:
                if table == self.model_py_path:
                    # toodo LucG tabling
                    self.__table = eval("mod." + self.model_py_path.split(".")[-1])
            except AttributeError as e:
                raise e
        Logger.instance().debug(self.table_key + " table class reloaded. Model: " + self.model_py_path)

    def set_table(self, model):
        self.__table = model

    def get_table(self):
        return self.__table

    @staticmethod
    def set_tables_properties(tables):
        """
        Import the models of the current execution and then associate models with TableInputOutputInformation objects.

        :param tables: the TableInputOutputInformation which need their table properties to be set.
        :type tables: ResultSet(TableInputOutputInformation)
        """
        # import models for avoid references errors between models when dealing with them
        TableInputOutputInformation.import_models(set([t.model_py_path for t in tables]))

        for table in tables:
            # keep track of the models used in static variable of TableInputOutputInformation
            TableInputOutputInformation.tablemodelnames.add(table.model_py_path)
            # Associate model with the TableInputOutputInformation object
            mod = importlib.import_module(table.model_py_path)
            table_model = eval("mod." + table.model_py_path.split(".")[-1])
            table.set_table(table_model)
            # keep track of table names used in static variable of TableInputOutputInformation
            TableInputOutputInformation.tablenames.add(table_model.__tablename__)
            SQLManager.instance().get_session().add(table)

    @staticmethod
    def get_execution_tables():
        """
        Return all the TableInputOutputInformation objects found in model TableInputOutputInformation.

        :return: ResultSet TableInputOutputInformation objects
        """
        session = SQLManager.instance().get_session()
        execution_id = session.query(func.max(ToolWrapper.execution_id))
        return session.query(TableInputOutputInformation).filter(TableInputOutputInformation.toolwrapper_id == ToolWrapper.id).filter(ToolWrapper.execution_id == execution_id).all()

    @staticmethod
    def import_models(model_names):
        """
        Import all the given models

        :param model_names: The path to the models
        :type model_names: Iterable(String)
        """
        for t in model_names:
            Logger.instance().debug("TableInputOutputInformation.import_models: importing " + str(t))
            importlib.import_module(t)

    def is_ready(self):
        """
        A TableInputOutputInformation object is ready if its table exists and contains entries.

        :return: bool if the table is ready
        """
        session = SQLManager.instance().get_session()
        try:
            results = session.query(self.__table).first()
            if results is None:
                Logger.instance().debug("The table " + self.table_key + " is empty.")
                return False
        except OperationalError as e:
            Logger.instance().debug("The table " + self.__table.__tablename__ + " doesn't exist.")
            return False
        except Exception as e:
            session.rollback()
            raise e
            # toodo LG twthread
        return True

    def __eq__(self, other):
        """
        Two TableInputOutputInformation object are equals if their table attributes belongs to the same class and if the associated table
        has the same content

        :param other: TableInputOutputInformation
        :return: boolean: True if the table attributes are the same, False if not
        """
        session = SQLManager.instance().get_session()
        if self.model_py_path != other.model_py_path or self.table_key != other.table_key:
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
        return "<class {}; tablename: {}; model_py_path: {}; used_at: {}>"\
            .format(self.__class__.__name__, self.table_key, self.model_py_path, self.mtime_epoch_millis)

    def __str__(self):
        return "<Table: " + self.table_key + "; model: " + self.model_py_path + ">"
