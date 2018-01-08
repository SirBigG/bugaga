import sqlalchemy
from sqlalchemy import orm

from web.models.base import Base

engine = sqlalchemy.create_engine('sqlite:///:memory:', echo=True)
# Create tables
Base.metadata.create_all(engine, checkfirst=True)
Session = orm.scoped_session(orm.sessionmaker())
Session.configure(bind=engine)
