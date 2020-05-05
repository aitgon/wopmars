from wopmars.Base import Base

from sqlalchemy import Column, Integer, String, Float


class Piece(Base):
    __tablename__ = __qualname__

    id = Column(Integer, primary_key=True, autoincrement=True)
    serial_number = Column(String, unique=True)
    type = Column(String)
    price = Column(Float)