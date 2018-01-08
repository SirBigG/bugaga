import sqlalchemy
from sqlalchemy import orm

from models.base import Base

engine = sqlalchemy.create_engine('sqlite:///:memory:')
# Create tables
Base.metadata.create_all(engine)
Session = orm.scoped_session(orm.sessionmaker())
Session.configure(bind=engine)
