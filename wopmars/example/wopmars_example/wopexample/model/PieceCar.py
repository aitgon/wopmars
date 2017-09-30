from sqlalchemy.sql.schema import ForeignKey

from wopmars.framework.database.Base import Base

from sqlalchemy import Column, Integer, String, Float


class PieceCar(Base):
    __tablename__ = "piece_car"

    id = Column(Integer, primary_key=True, autoincrement=True)
    car_serial_number = Column(String, unique=True)
    bodywork_serial_number = Column(String, ForeignKey("piece.serial_number"))
    engine_serial_number = Column(String, ForeignKey("piece.serial_number"))
    wheel_serial_number = Column(String, ForeignKey("piece.serial_number"))
    price = Column(Float)
