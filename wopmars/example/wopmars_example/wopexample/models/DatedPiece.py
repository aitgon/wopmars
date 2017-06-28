from sqlalchemy.sql.sqltypes import Date
from sqlalchemy import Column

from wopexample.models.Piece import Piece


class DatedPiece(Piece):
    date = Column(Date)
