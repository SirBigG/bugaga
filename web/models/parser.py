from datetime import datetime

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, JSON

Base = declarative_base()


class ParserMap(Base):
    __tablename__ = 'parsermap'

    id = Column(Integer, primary_key=True)
    category_id = Column(Integer, ForeignKey('category.id'), nullable=False)
    link = Column(String, nullable=False)
    map = Column(String, nullable=False)
    type = Column(Integer, nullable=False)


class ParsedData(Base):
    __tablename__ = 'parseddata'

    id = Column(Integer, primary_key=True)
    data = Column(JSON, nullable=False)
    hash = Column(String(255), nullable=False)
    category_id = Column(Integer, ForeignKey('category.id'), nullable=False)
    created = Column(DateTime, default=datetime.now)
