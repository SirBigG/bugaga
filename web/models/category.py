
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String

from sqlalchemy_mptt.mixins import BaseNestedSets


Base = declarative_base()


class Category(Base, BaseNestedSets):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    slug = Column(String(255), unique=True, nullable=False)
    title = Column(String(255), nullable=False)

    def __repr__(self):
        return '<Category(slug=%s, title=%s)' % (self.slug, self.title)
