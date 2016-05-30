"""
Module containing Base class
"""
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
# Todo ask lionel SQLlite gère le multi-session mais pose un verrou sur la base entière quand une sessiion est en
# train d'écrire