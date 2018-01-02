import db

from web.models.parser import ParserMap

from .handlers import ParseHandler


def parse_items():
    session = db.Session()
    for i in session.query(ParserMap).filter(ParserMap.is_active is True):
        ParseHandler(i, session).create_items()
    # closed session finally
    session.close()


if __name__ == "__main__":
    parse_items()
