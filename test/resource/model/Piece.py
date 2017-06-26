from wopmars.main.tagc.framework.bdd.Base import Base

from sqlalchemy import Column, Integer, String, Float


class Piece(Base):
    __tablename__ = "Piece"

    id = Column(Integer, primary_key=True, autoincrement=True)
    serial_number = Column(String(255), unique=True)
    type2 = Column(String(255))
    price = Column(Float)

