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
    title = Column(String, nullable=False)
    category = Column(String, nullable=False)
    text = Column(Text, nullable=False)
    accords = Column(Text, nullable=False, default='')

    records = relationship('Record', order_by='Record.id', back_populates='bhajan')

    def __repr__(self):
        return ("<Bhajan(id={0.id}, title='{0.title}', category='{0.category}', "
                "text='{0.text}', accords='{0.accords}')>".format(self))


class Record(Base):
    __tablename__ = 'records'

    id = Column(Integer, primary_key=True)
    artist = Column(String, nullable=False)
    path = Column(String, nullable=False)
    bhajan_id = Column(Integer, ForeignKey('bhajans.id'), nullable=False)

    bhajan = relationship('Bhajan', back_populates='records')

    def __repr__(self):
        return "<Record(id={0.id}, artist='{0.artist}', path='{0.path}', bhajan_id={0.bhajan_id})>" \
               .format(self)


# run configure_mappers after defining all of the models to ensure
# all relationships can be setup
configure_mappers()
