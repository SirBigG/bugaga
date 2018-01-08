from db import Session

from models.parser import ParserMap

from parser.handlers import ParseHandler


def parse_items():
    session = Session()
    for i in session.query(ParserMap).filter(ParserMap.is_active == 1):
        ParseHandler(i, session).create_items()
    # closed session finally
    session.close()


if __name__ == "__main__":
    parse_items()
