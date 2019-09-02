from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from .base import Base


class User(Base):
    from models.category import Category
    __tablename__ = 'tusers'

    id = Column(Integer, primary_key=True)
    date_joined = Column(DateTime, default=datetime.now())
    telegram_key = Column(String(255), nullable=True)
    temp_key = Column(String(255), nullable=True)
    is_subscribed = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    categories = relationship(Category, secondary="user_category_association")

    def __repr__(self):
        return f'<User(username={self.telegram_key})>'


class UserCategoryAssociation(Base):
    from models.category import Category
    __tablename__ = 'user_category_association'

    user_id = Column(Integer, ForeignKey(User.id), primary_key=True)
    category_id = Column(Integer, ForeignKey(Category.id), primary_key=True)
