from sqlalchemy import Column, Integer, String, Boolean

from sqlalchemy_mptt.mixins import BaseNestedSets

from .base import Base


class Category(Base, BaseNestedSets):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    slug = Column(String(255), unique=True, nullable=False)
    title = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)

    def __repr__(self):
        return f'<Category(slug={self.slug}, title={self.title})>'
