from wopmars.framework.database.Base import Base

from sqlalchemy import Column, String, Integer, SmallInteger
from sqlalchemy import UniqueConstraint

class SNP(Base):
    __tablename__ = 'SNP'
    __table_args__ = (
            UniqueConstraint('chrom', 'position'),
            UniqueConstraint('rsid'),
            )

    id = Column(Integer, primary_key=True, autoincrement=True)
    chrom = Column(SmallInteger, nullable=False)
    position = Column(Integer, nullable=False)
    rsid = Column(Integer, nullable=False)

