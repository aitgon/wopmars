from wopmars.Base import Base
from sqlalchemy import Column, String, BigInteger, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql.ddl import DDL
from wopmars.SQLManager import SQLManager

class TableModificationTime(Base):
    """
    The TableModificationTime model contains the table names of the workflow and their mtime_epoch_millis of last modification. The table
    ``wom_modification_table`` contains the following fields:

    - table_name: VARCHAR(255) - primary key - the is_input of the table
    - mtime_epoch_millis: INTEGER - unix mtime_epoch_millis [ms] of last modification of the table
    """

    __tablename__ = "wom_{}".format(__qualname__)

    table_name = Column(String(255), primary_key=True)
    mtime_human = Column(DateTime, nullable=False)
    mtime_epoch_millis = Column(BigInteger, nullable=False)

    # One table_io_info has one table_modif_time
    relation_tablemodiftime_to_tableioinfo = relationship("TableInputOutputInformation", back_populates="relation_tableioinfo_to_tablemodiftime")

    def __repr__(self):
        return "<Modification on " + str(self.table_name) + ": " + str(self.mtime_epoch_millis) + ">"

    @classmethod
    def create_triggers(cls):
        """
        Create an INSERT, UPDATE, DELETE trigger on the models created by the user in order to store the modifications mtime_epoch_millis.
        """
        stmt_list = ["INSERT", "UPDATE", "DELETE"]
        for user_table_name in Base.metadata.tables:
            if user_table_name[:4] != "wom_":
                for statement in stmt_list:
                    data={"statement": str(statement), "user_table_name": user_table_name, "wom_table_name": "wom_{}".format(cls.__qualname__)}
                    if SQLManager.instance().__dict__['d_database_config']['db_connection'] == 'sqlite':
                        sql_trigger = "CREATE TRIGGER IF NOT EXISTS {user_table_name}_{statement} " \
                              "AFTER {statement} ON {user_table_name} BEGIN UPDATE {wom_table_name} " \
                              "SET mtime_epoch_millis = CAST((julianday('now') - 2440587.5)*86400000 AS INTEGER), " \
                              "mtime_human = datetime('now', 'localtime') " \
                                      "WHERE table_name = '{user_table_name}'; END;".format(**data)
                    # elif SQLManager.instance().__dict__['d_database_config']['db_connection'] == 'mysql':
                    #     sql_trigger = "CREATE TRIGGER IF NOT EXISTS {table_key}_{statement} AFTER {statement} " \
                    #       "ON {table_key} for each row UPDATE wom_table_modification_time SET " \
                    #                   "mtime_epoch_millis = ROUND(UNIX_TIMESTAMP(CURTIME(4)) * 1000) " \
                    #       "WHERE table_key = '{table_key}';".format(**data)
                    #     obj_ddl = DDL(sql_trigger)
                    #     SQLManager.instance().create_trigger(Base.metadata.tables[table_key], obj_ddl)
                    # elif SQLManager.instance().__dict__['d_database_config']['db_connection'] == 'postgresql':
                    #     sql_trigger = """
                    #         CREATE OR REPLACE FUNCTION {table_key}_{statement}() RETURNS TRIGGER AS ${table_key}_{statement}$
                    #         BEGIN
                    #         UPDATE wom_table_modification_time SET mtime_epoch_millis = extract(epoch from now())*1000 WHERE table_key = '{table_key}';
                    #         RETURN NULL; -- result is ignored since this is an AFTER trigger
                    #         END;
                    #         ${table_key}_{statement}$ LANGUAGE plpgsql;
                    #         DROP TRIGGER IF EXISTS {table_key}_{statement} ON "{table_key}";
                    #         CREATE TRIGGER {table_key}_{statement} AFTER INSERT ON "{table_key}"
                    #         FOR EACH ROW EXECUTE PROCEDURE {table_key}_{statement}();
                    #         """.format(**data)
                    obj_ddl = DDL(sql_trigger)
                    SQLManager.instance().create_trigger(Base.metadata.tables[user_table_name], obj_ddl)
