from sqlalchemy.sql.sqltypes import Date
from sqlalchemy import Column

from wopexamplesnp.model.Piece import Piece


class DatedPiece(Piece):
    date = Column(Date)
