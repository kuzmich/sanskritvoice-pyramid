from sqlalchemy import (
    Column,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import configure_mappers

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


# run configure_mappers after defining all of the models to ensure
# all relationships can be setup
configure_mappers()
