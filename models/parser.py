from datetime import datetime

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship, backref


from .base import Base

class ParserMap(Base):
    from models.category import Category
    __tablename__ = 'parsermap'

    id = Column(Integer, primary_key=True)
    category_id = Column(Integer, ForeignKey(Category.id), nullable=False)
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
    category_id = Column(Integer, ForeignKey(Category.id), nullable=False)
    created = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return f'<ParsedItem(id={self.id}, hash={self.hash})>'
