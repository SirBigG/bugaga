import sqlalchemy
from sqlalchemy import orm

Session = orm.scoped_session(orm.sessionmaker())
engine = sqlalchemy.create_engine('sqlite:///:memory:')
Session.configure(bind=engine)
