from wopmars.framework.database.Base import Base

from sqlalchemy import Column, String, Integer
from sqlalchemy import UniqueConstraint

class SNP(Base):
    __tablename__ = 'SNP'
    __table_args__ = (
            UniqueConstraint('chrom', 'position'),
            UniqueConstraint('rsid'),
            )

    id = Column(Integer, primary_key=True, autoincrement=True)
    chrom = Column(String(255), nullable=False)
    position = Column(Integer, nullable=False)
    rsid = Column(String(255), nullable=False)

