"""
Module containing the WopmarsSession class.
"""
from sqlalchemy.sql.elements import ClauseElement

from wopmars.WopmarsQuery import WopmarsQuery
from wopmars.utils.Logger import Logger


class WopmarsSession:
    """
    The class WopmarsSession is used in order to allow the Toolwrapper Developer to access the database.

    This class is a pivot between the Toolwrapper Developer and the SQLManager. Every call to the database has to pass
    through the SQLManager but the developer has only access to the session.
    """

    def __init__(self, session, manager):
        """
        :param session: contains a SQLAlchemy session
        :param manager: contains the SQLManager
        """
        self.__manager = manager
        self.__session = session

    def commit(self):
        """
        Validate changes on the database. Should be used when everything is ok.
        """
        if self.something():
            Logger.instance().debug(str(self.__session) + " is about to commit.")
            Logger.instance().debug("Operations to be commited in session" + str(self.__session) + ": \n\tUpdates:\n\t\t" +
                                    "\n\t\t".join([str(k) for k in self.__session.dirty]) +
                                    "\n\tInserts:\n\t\t" +
                                    "\n\t\t".join([str(k) for k in self.__session.new]))
            # call on SQLManager commit method to use the lock
            self.__manager.commit(self.__session)

    def rollback(self):
        """
        Rollback changes on the database. Should be used in case of error.
        :return:
        """
        Logger.instance().debug("Operations to be rollbacked in session" + str(self.__session) + ": \n\tUpdates:\n\t\t" +
                                "\n\t\t".join([str(k) for k in self.__session.dirty]) +
                                "\n\tInserts:\n\t\t" +
                                "\n\t\t".join([str(k) for k in self.__session.new]))
        # call on SQLManager commit method to use the lock
        self.__manager.rollback(self.__session)

    def query(self, table):
        """
        Return a WopmarsQuery used for querying database using the ORM.

        :param table: The mapper object on which you want to query.
        :return: WopmarsQuery on the desired table and bind to the current session.
        """
        return WopmarsQuery(table, session=self.__session)

    def add(self, item):
        """
        Add an item to the current session. To write the change on the database, don't forget to commit.

        :param item: a mapper object
        """
        self.__session.add(item)

    def add_all(self, collection):
        """
        Add a collection of items to the current session. To write the change on the database, don't forget to commit.

        :param collection: collection of mappers
        """
        self.__session.add_all(collection)

    def delete(self, entry):
        """
        Delete an entry from the database. To write the change on the database, don't forget to commit.

        :param entry: A mapper object already existent in the database.
        """
        self.__session.delete(entry)

    def delete_content(self, table):
        """
        Delete the content of a given table.

        :param table: A mapper object representing the table in which the content should be deleted.
        """
        Logger.instance().debug("Deleting content of table " + table.__tablename__ + "...")
        self.__manager.execute(self.__session, table.__table__.delete())
        Logger.instance().debug("Content of table " + table.__tablename__ + " deleted.")

    def execute(self, statement, *args, **kwargs):
        """
        Execute a statement of the given values.

        :param statement: SQLAlchemy statement (insert, delete, etc..)
        :param args: dict of values
        :param kwargs: exploded dict of values
        :return: return the result of the execution of the statement
        """
        Logger.instance().debug("WopmarsSession.execute(" + str(statement) + ", " + str(args) + ", " + str(kwargs) + ")")
        return self.__manager.execute(self.__session, statement, *args, **kwargs)

    def close(self):
        """
        Close the current session. Shouldn't be used.

        :return:
        """
        self.__session.close()

    def _session(self):
        """
        Return the SQLAlchemy session shouldn't be used by the ToolWrapper Developper.
        """
        return self.__session

    def something(self):
        """
        Check if there is something in the session.

        :return: Bool saying if there is something in the session.
        """
        return bool(self.__session.new) or bool(self.__session.dirty) or bool(self.__session.deleted)

    def get_or_create(self, model, defaults=None, **kwargs):
        """
        This method allows to check if an entry exist in database and if not, create it. It also return a boolean
        which says if the entry has been created (True) or not (False)

        :param model: A SQLAlchemy model
        :param defaults: Dict containing the default parameter to use in fields if the entry doesn't exist.
        :param kwargs: Specify the values of the fields which are looked for. Create them if not.

        :return: tuple: (instance of the created entry, boolean)
        """
        instance = self.__session.query(model).filter_by(**kwargs).first()
        if instance:
            return instance, False
        else:
            params = dict((k, v) for k, v in kwargs.items() if not isinstance(v, ClauseElement))
            params.update(defaults or {})
            instance = model(**params)
            self.__session.add(instance)
            return instance, True

    # def pandas_to_sql(self, df, tablename, *args, **kwargs):
    #     """
    #     Interface for using the to_sql method from pandas dataframes.
    #
    #     :param df: pandas dataframe
    #     :type df: DataFrame
    #     :param tablename: the is_input of the table on which you want to perform operations
    #     :type tablename: str
    #     :param args: args of the conventionnal pandas.to_sql method
    #     :param kwargs: kwargs of the conventionnal pandas.to_sql method
    #     """
    #     self.__manager.pandas_to_sql(df, tablename, *args, **kwargs)
    #
    # def pandas_read_sql(self, sql, *args, **kwargs):
    #     """
    #     Interface for using the read_sql method from pandas dataframes.
    #
    #     :param sql: the sql query to perform on the database
    #     :type sql: str
    #     :param args: args of the conventionnal pandas.read_sql method
    #     :param kwargs: kwargs of the conventionnal pandas.read_sql method
    #     :return: Pandas dataframe contianing the result
    #     """
    #     return self.__manager.pandas_read_sql(sql, *args, **kwargs)

