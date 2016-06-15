"""
Module containing Base class
"""
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine

s_database_name = "/home/giffon/db.sqlite"
Engine = create_engine('sqlite:///' + s_database_name, echo=False)
Base = declarative_base(bind=Engine)
