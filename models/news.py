from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime

from .base import Base


class News(Base):
    __tablename__ = 'news'

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(String, nullable=False)
    image = Column(String, nullable=True)
    created = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return f'<News(id={self.id}, title={self.title})>'
