from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from settings import settings


Engine = create_engine(settings.ENGINE)
Session = sessionmaker(bind=Engine)
