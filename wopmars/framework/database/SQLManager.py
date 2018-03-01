"""
Module containing the SQLManager class.
"""
# import pandas
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine
from sqlalchemy.schema import sort_tables
from sqlalchemy import event

from wopmars.framework.database.Base import Base
from wopmars.framework.database.WopMarsSession import WopMarsSession
from wopmars.utils.Logger import Logger
from wopmars.utils.OptionManager import OptionManager
from wopmars.utils.RWLock import RWLock
from wopmars.utils.Singleton import SingletonMixin
from wopmars.utils.exceptions.WopMarsException import WopMarsException


class SQLManager(SingletonMixin):
    """
    The class SQLManager is responsible of all operations performed on the database.

    The SQLManager is a synchronized Singleton which may be accessible from any thread, at any time. This is allowed
    by the SingletonMixin superclass and a read/write lock.

    Provides a WopMarsSession through the method "get_session". The session is used to perform calls to the database.
    Provides the engine if necessary through "get_engine".
    Allows commiting and rollbacking operations of a given session through methods "commit" and "rollback".
    Allows querying operations from a given query: all, one, first, count, one_or_none, scalar. Through "result_factory".
    Allows executing statements through the "execute" method.
    Allows droping and creating tables from table names ("create" and "drop"), list of table models ("drop_table_list")
    and all ("create_all" and "drop_all").
    """
    wom_table_names = [
        "wom_type",
        "wom_modification_table",
        "wom_execution",
        "wom_rule",
        "wom_table",
        "wom_file",
        "wom_option"
    ]

    def __init__(self):
        """
        The constructor of the SQLManager is supposed to be called once in the whole execution, thanks to the
        SingletonMixin inheritance.

        The constructor create the engine at the localization provided by the user. The option "connect_args" is set to
        False.

        The "PRAGMA foreign_keys=ON" statement is executed here and allows to enforce foreign_keys constraints.

        The Session attribute is a object of class "Type" and allows to make a scoped session bound to the engine on demand.
        The autocommit is set to False and the autoflush, to True.

        The lock is initialized here thanks to the RW lock class and will be used to overide the behaviour of sqlite
        to assess the access to the databse without using the queue of SQLite, bound at 4 sec wait before error.
        """
        s_database_url = OptionManager.instance()["--database"]
        self.d_database_config = {'db_connection': None, 'db_database': None, 'db_url': s_database_url}
        self.d_database_config['db_connection'] = s_database_url.split("://")[0]
        if self.d_database_config['db_connection'] == "sqlite":
            self.d_database_config['db_database'] = s_database_url.replace("sqlite:///", "")
        # echo=False mute the log of database
        # connect_args have been necessary because of the accession of the same objects in different Threads.
        if self.d_database_config['db_connection']=="sqlite":
            self.__engine = create_engine(self.d_database_config['db_url'], echo=False, connect_args={'check_same_thread': False})
        else:
            self.__engine = create_engine(self.d_database_config['db_url'], echo=False)
        # Below, between "###", code copy-pasted from this post
        # http://stackoverflow.com/questions/2614984/sqlite-sqlalchemy-how-to-enforce-foreign-keys/7831210#7831210
        # enforce foreign key constraints
        ###
        def _fk_pragma_on_connect(dbapi_con, con_record):
            if self.d_database_config['db_connection'] == "sqlite":
                dbapi_con.execute('pragma foreign_keys=ON')

        event.listen(self.__engine, 'connect', _fk_pragma_on_connect)
        ###

        # I don't know why I have used the autoflush=True
        self.__Session = scoped_session(sessionmaker(bind=self.__engine, autoflush=True, autocommit=False))
        # The lock
        self.__lock = RWLock()

    def get_engine(self):
        """
        Return the engine of the current execution.

        :return: engine
        """
        return self.__engine

    def get_session(self):
        """
        Return a WopmarsSession associated with this SQLmanager.

        :return: WopMarsSession
        """
        session = WopMarsSession(self.__Session(), self)
        return session

    def commit(self, session):
        """
        Commit the current session.

        The SQLManager wrap the sqlite queue for commiting operations on database in order to do not trigger the error due
        to the time-out operations.

        This is done thanks to a read_write_lock: sqlmanager is a synchronized singleton with synchronized methods.

        :param session: SQLAlchemy session object
        """
        try:
            Logger.instance().debug(str(session) + " want the write lock on SQLManager.")
            self.__lock.acquire_write()
            Logger.instance().debug(str(session) + " has taken the write lock on SQLManager.")
            session.commit()
            Logger.instance().debug(str(session) + " has been commited.")
        finally:
            # Always release the lock
            self.__lock.release()
            Logger.instance().debug(str(session) + " has released the write lock on SQLManager.")

    def result_factory(self, query, method):
        """
        Return the result of the query, using the demanded method.

        The result_factory wrap the methods for querying database:
          - all
          - first
          - one
          - one_or_none
          - scalar
          - count

        This is necessary to use the ReadLock of WopMars instead of the one from SQLite.

        :param query: The query object, ready to be performed.
        :param method: String signifying the method which have to be used for querying database
        :return: The result of the query.
        """
        result = None
        try:
            Logger.instance().debug("Executing query on session " + str(query.session) + ": \n" + str(query) + ";")
            Logger.instance().debug("WopMarsQuery " + str(query.session) + " want the read-lock on SQLManager")
            self.__lock.acquire_read()
            Logger.instance().debug("\"" + str(query.session) + "\" has taken the read lock on SQLManager.")
            # switch case according to the demanded method.
            # in each condition, we call the superclass associated method: superclass is Query from sqlalchemy
            if method == "all":
                result = super(query.__class__, query).all()
            elif method == "one":
                result = super(query.__class__, query).one()
            elif method == "first":
                result = super(query.__class__, query).first()
            elif method == "count":
                result = super(query.__class__, query).count()
            elif method == "one_or_none":
                result = super(query.__class__, query).one_or_none()
            elif method == "scalar":
                result = super(query.__class__, query).scalar()
            else:
                raise WopMarsException("Error while querying the database.",
                                       "Demanded operation doesn't exist: " + str(method))
        finally:
            # Always release the lock
            self.__lock.release()
            Logger.instance().debug("\"" + str(query.session) + "\" has released the read lock on SQLManager.")
        return result

    def execute(self, session, statement, *args, **kwargs):
        """
        Allow to execute a statement object on the given session.

        :param session: SQLAlchemy session object.
        :param statement: SQLAlchemy statement object.
        """
        Logger.instance().debug("SQLManager.execute(" + str(session) + ", " + str(statement) + ", " +
                                    str(args) + ", " + str(kwargs) + ")")
        try:
            Logger.instance().debug(str(session) + " want the write lock on SQLManager for statement \"" + str(statement) + "\"")
            self.__lock.acquire_write()
            Logger.instance().debug(str(session) + " has taken the write lock on SQLManager.")
            return session.execute(statement, *args, **kwargs)
        finally:
            # Always release the lock
            self.__lock.release()
            Logger.instance().debug(str(session) + " has released the write lock on SQLManager.")

    def rollback(self, session):
        """
        Rollback the given session.

        The SQLManager wrap the sqlite queue for rollbacking operations on database in order to do not trigger the error due
        to the time-out operations.

        This is done thanks to a read_write_lock: sqlmanager is a synchronized singleton with synchronized methods.

        :param session: SQLAlchemy session object
        """
        try:
            Logger.instance().debug(str(session) + " want the write lock on SQLManager.")
            self.__lock.acquire_write()
            Logger.instance().debug(str(session) + " has taken the write lock on SQLManager.")
            session.rollback()
            Logger.instance().debug(str(session) + " has been rollbacked.")
        finally:
            # Always release the lock
            self.__lock.release()
            Logger.instance().debug(str(session) + " has released the write lock on SQLManager.")

    def drop_all(self):
        """
        Use the declarative Base to drop all tables found. Should only be used for testing purposes.
        """
        try:
            self.__lock.acquire_write()
            Logger.instance().debug("Dropping all tables...")
            Base.metadata.drop_all(self.__engine)
        finally:
            # Always release the lock
            self.__lock.release()

    def create_all(self):
        """
        Use the declarative Base to create all tables found.

        If you want to create a table, you should be sure that it has been imported first.
        """
        try:
            self.__lock.acquire_write()
            Logger.instance().debug("Creating all tables...")
            Base.metadata.create_all(self.__engine)
            # Always release the lock
        finally:
            self.__lock.release()

    def create(self, tablename):
        """
        Use the declarative Base to create a table from its tablename.

        The tablename is the name of the base represented in the databse (independent of the Table model)
        :param tablename:
        """
        try:
            self.__lock.acquire_write()
            Logger.instance().debug("SQLManager.create(" + str(tablename) + "): create table " + str(tablename))
            Base.metadata.tables[tablename.split(".")[-1]].create(self.__engine, checkfirst=True)
        finally:
            # Always release the lock
            self.__lock.release()

    def drop(self, tablename):
        """
        Use the declarative Base to drop a table from its tablename.

        The tablename is the name of the base represented in the databse (independent of the Table model)
        :param tablename:
        """
        try:
            self.__lock.acquire_write()
            # todo tabling
            Logger.instance().debug("SQLManager.drop(" + str(tablename) + "): drop table " + str(tablename))
            Base.metadata.tables[tablename.split(".")[-1]].drop(self.__engine, checkfirst=True)
        finally:
            # Always release the lock
            self.__lock.release()

    def drop_table_list(self, list_str_table):
        """
        Remove a list of tables from the list of their tablenames.

        :param list_str_table: [String] the name of the tables.
        """
        # Get the list of Table objects from tablenames, then sort them according to their relationships / foreignkeys
        # and take the reverse to delete them in the right order (reverse of the correct order for creating them)
        # todo tabling
        list_obj_table = reversed(sort_tables([Base.metadata.tables[tablename.split(".")[-1]] for tablename in list_str_table]))
        try:
            self.__lock.acquire_write()
            for t in list_obj_table:
                Logger.instance().debug("SQLManager.drop_table_list(" + str(list_str_table) + "): drop table " + str(t.name))
                t.drop(self.__engine, checkfirst=True)
        finally:
            # Always release the lock
            self.__lock.release()

    def drop_table_content_list(self, list_str_table):
        """
        Remove a list of tables from the list of their tablenames.

        :param list_str_table: [String] the name of the tables.
        """
        session = self.get_session()
        # Get the list of Table objects from tablenames, then sort them according to their relationships / foreignkeys
        # and take the reverse to delete them in the right order (reverse of the correct order for creating them)
        list_obj_table = reversed(
            sort_tables([Base.metadata.tables[tablename.split(".")[-1]] for tablename in list_str_table]))
        for t in list_obj_table:
            Logger.instance().debug(
                "SQLManager.drop_table_content_list(" + str(list_str_table) + "): drop table content " + str(t.name))
            self.execute(session._session(), t.delete())

    # def pandas_to_sql(self, df, *args, **kwargs):
    #     """
    #     Execute the `DataFrame.to_sql <http://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.to_sql.html>`_ function from pandas.DataFrame.
    #
    #     :param df: The DataFrame to insert in database.
    #     :type df: `pandas.DataFrame <http://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.html>`_
    #     :param args: The conventional arguments for the pandas.to_sql function.
    #     :param kwargs: The conventional key arguments for the pandas.to_sql function.
    #     """
    #     try:
    #         self.__lock.acquire_write()
    #         df.to_sql(*args, **kwargs)
    #         Logger.instance().debug("SQLManager.pandas_to_sql: Adding dataframe to database")
    #     finally:
    #         self.__lock.release()
    #
    # def pandas_read_sql(self, *args, **kwargs):
    #     """
    #     Execute the `pandas.read_sql <http://pandas.pydata.org/pandas-docs/stable/generated/pandas.read_sql.html?highlight=sql>`_ function
    #
    #     :param args: The conventional arguments for the pandas.read_sql function.
    #     :param kwargs: The conventional key arguments for the pandas.read_sql function.
    #     :return DataFrame: The dataframe containing the results of the query.
    #     """
    #     try:
    #         self.__lock.acquire_read()
    #         df = pandas.read_sql(*args, **kwargs)
    #         Logger.instance().debug("SQLManager.read_sql: Reading database using pandas")
    #     finally:
    #         self.__lock.release()
    #     return df

    def create_trigger(self, table, ddl):
        """
        Create a Trigger after creating a given table.

        :param table:
        :type table: `Table <http://docs.sqlalchemy.org/en/latest/core/metadata.html#sqlalchemy.schema.Table>`_
        :param ddl:
        :type ddl: `DDL <http://docs.sqlalchemy.org/en/latest/core/ddl.html#sqlalchemy.schema.DDL>`_
        """
        try:
            self.__lock.acquire_write()
            event.listen(table, 'after_create', ddl)
        finally:
            self.__lock.release()

