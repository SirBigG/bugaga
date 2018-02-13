import sqlalchemy
from sqlalchemy import orm

# Import all models for tables create.
from models import *
from models.base import Base

Engine = sqlalchemy.create_engine('sqlite:///:memory:')
# Create tables
Base.metadata.create_all(Engine)
Session = orm.scoped_session(orm.sessionmaker())
Session.configure(bind=Engine)
