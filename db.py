import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from settings import settings


if 'WORKSPACE' in os.environ and os.environ['WORKSPACE'] == 'DEV':
    from tests.common import Session, Engine
    Engine = Engine
    Session = Session
else:
    Engine = create_engine(settings.ENGINE)
    Session = sessionmaker(bind=Engine)
