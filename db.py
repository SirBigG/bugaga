import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from settings import settings

if 'WORKSPACE' in os.environ and os.environ['WORKSPACE'] == 'DEV':
    Engine = create_engine(settings.ENGINE)
    Session = sessionmaker(bind=Engine)
else:
    Engine = create_engine(settings.ENGINE,
                           pool_size=10,
                           max_overflow=2,
                           pool_recycle=300,
                           pool_pre_ping=True,
                           pool_use_lifo=True)
    Session = sessionmaker(bind=Engine)
