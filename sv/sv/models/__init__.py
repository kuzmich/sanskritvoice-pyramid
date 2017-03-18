from sqlalchemy import (
    Column,
    Index,
    Integer,
    String,
    Text,
    ForeignKey
)
from sqlalchemy.orm import configure_mappers, relationship

from .meta import Base


# import or define all models here to ensure they are attached to the
# Base.metadata prior to any initialization routines

class Bhajan(Base):
    __tablename__ = 'bhajans'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    category = Column(String)
    text = Column(Text)
    accords = Column(Text)

    records = relationship('Record', order_by='Record.id', back_populates='bhajan')


class Record(Base):
    __tablename__ = 'records'

    id = Column(Integer, primary_key=True)
    artist = Column(String)
    path = Column(String)
    bhajan_id = Column(Integer, ForeignKey('bhajans.id'))

    bhajan = relationship('Bhajan', back_populates='records')


# run configure_mappers after defining all of the models to ensure
# all relationships can be setup
configure_mappers()
