from wopmars.framework.database.Base import Base

from sqlalchemy import Column, Integer, String, Float


class Piece(Base):
    __tablename__ = "piece"

    id = Column(Integer, primary_key=True, autoincrement=True)
    serial_number = Column(String, unique=True)
    type = Column(String)
    price = Column(Float)