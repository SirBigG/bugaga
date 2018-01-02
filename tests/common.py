import sqlalchemy
from sqlalchemy import orm

from web.models.base import Base
# from web.models.category import Base as CBase

engine = sqlalchemy.create_engine('sqlite:///:memory:')
# Create tables
Base.metadata.create_all(engine, checkfirst=True)
Session = orm.scoped_session(orm.sessionmaker())
Session.configure(bind=engine)


# CBase.metadata.create_all(engine)
