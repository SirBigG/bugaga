from datetime import datetime

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Float
from sqlalchemy.orm import relationship, backref


from .base import Base

class ParserMap(Base):
    from models.category import Category
    __tablename__ = 'parsermap'

    id = Column(Integer, primary_key=True)
    category_id = Column(Integer, ForeignKey(Category.id), nullable=True)
    category = relationship(Category)  # , backref=backref('category', lazy='dynamic'))
    host = Column(String(255), nullable=False)
    link = Column(String, nullable=False)
    map = Column(String, nullable=False)
    root = Column(String(255))
    type = Column(Integer, nullable=False)
    last_crawling = Column(DateTime)
    period = Column(Integer, nullable=False)
    period_type = Column(String(25), nullable=False)
    is_active = Column(Boolean, default=True)

    def __repr__(self):
        return f'<ParserMap(id={self.id}, link={self.link})>'


class ParsedItem(Base):
    from models.category import Category
    __tablename__ = 'parseditem'

    id = Column(Integer, primary_key=True)
    data = Column(String, nullable=False)
    hash = Column(String(255), nullable=False)
    category_id = Column(Integer, ForeignKey(Category.id), nullable=True)
    created = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return f'<ParsedItem(id={self.id}, hash={self.hash})>'


class AdvertParserMap(Base):
    __tablename__ = 'advertparsemap'

    id = Column(Integer, primary_key=True)
    host = Column(String(255), nullable=False)
    link = Column(String, nullable=False)
    map = Column(String, nullable=False)
    root = Column(String(255))
    # Parser type html xml etc.
    type = Column(Integer, nullable=False)
    # Parse data type is list for links parse or detail
    # 1 - Links
    # 2 - detail
    content_type = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True)

    def __repr__(self):
        return f'<OrderParserMap(id={self.id}, host={self.host})>'


class Link(Base):
    __tablename__ = 'link'

    id = Column(Integer, primary_key=True)
    link = Column(String, nullable=False)
    is_parsed = Column(Boolean, default=False)

    def __repr__(self):
        return f'<Link(id={self.id}, link={self.link})>'


class Advert(Base):
    __tablename__ = 'advert'

    id = Column(Integer, primary_key=True)
    data = Column(String, nullable=False)
    link = Column(String, nullable=False)
    hash = Column(String(500), nullable=True)
    category = Column(Integer, nullable=True)
    location = Column(Integer, nullable=True)
    price = Column(Float, nullable=True)
    created = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return f'<Advert(id={self.id}, hash={self.hash})>'
