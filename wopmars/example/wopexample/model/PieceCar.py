from sqlalchemy.sql.schema import ForeignKey

from wopmars.Base import Base

from sqlalchemy import Column, Integer, String, Float


class PieceCar(Base):
    __tablename__ = __qualname__

    id = Column(Integer, primary_key=True, autoincrement=True)
    car_serial_number = Column(String, unique=True)
    bodywork_serial_number = Column(String, ForeignKey("Piece.serial_number"))
    engine_serial_number = Column(String, ForeignKey("Piece.serial_number"))
    wheel_serial_number = Column(String, ForeignKey("Piece.serial_number"))
    price = Column(Float)
