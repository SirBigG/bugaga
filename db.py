from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from settings import settings


Engine = create_engine("postgresql://%s:%s@%s/%s" % settings.DB_SETTINGS)
# Engine = create_engine('sqlite:///db.sqlite3', echo=True)
Session = sessionmaker(bind=Engine)
