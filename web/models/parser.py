from datetime import datetime

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, JSON, Boolean

from .base import Base


class ParserMap(Base):
    __tablename__ = 'parsermap'

    id = Column(Integer, primary_key=True)
    category_id = Column(Integer, ForeignKey('сategory.id'), nullable=False)
    link = Column(String, nullable=False)
    map = Column(JSON, nullable=False)
    root = Column(String(256))
    type = Column(Integer, nullable=False)
    last_crawling = Column(DateTime)
    period = Column(Integer, nullable=False)
    period_type = Column(String(25), nullable=False)
    is_active = Column(Boolean, default=True)


class ParsedItem(Base):
    __tablename__ = 'parseditem'

    id = Column(Integer, primary_key=True)
    data = Column(JSON, nullable=False)
    hash = Column(String(255), nullable=False)
    category_id = Column(Integer, ForeignKey('category.id'), nullable=False)
    created = Column(DateTime, default=datetime.now)
