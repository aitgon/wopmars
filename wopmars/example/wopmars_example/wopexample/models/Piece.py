from sqlalchemy import Column, Integer, String, Float

from wopmars.framework import Base


class Piece(Base):
    __tablename__ = "piece"

    id = Column(Integer, primary_key=True, autoincrement=True)
    serial_number = Column(String, unique=True)
    type = Column(String)
    price = Column(Float)