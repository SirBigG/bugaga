#!/usr/local/bin/python

import logging
import json

from db import Session

from models.parser import ParserMap, AdvertParserMap, ParsedItem
from models.auth import User

from parser.handlers import ParseHandler, LinkParseHandler, AdvertParseHandler

from processing import processing


def parse_items():
    session = Session()
    _items_count = 0
    try:
        for i in session.query(ParserMap).filter(ParserMap.is_active.is_(True)):
            try:
                _items = ParseHandler(i, session).create_items()
                _items_count += len(_items)
            except Exception as e:
                logging.error(f"Error - {e}. Host - {i.host}")
    except Exception as e:
        logging.error(f"Error in parse_items - {e}")
    finally:
        # closed session finally
        session.close()
    return _items_count


def parse_links():
    session = Session()
    try:
        for i in session.query(AdvertParserMap).filter(AdvertParserMap.is_active.is_(True),
                                                       AdvertParserMap.content_type == 1):
            LinkParseHandler(i, session).create_items()
    except Exception as e:
        logging.error(f"Error in parse_links - {e}")
    finally:
        session.close()


def parse_advert():
    session = Session()
    try:
        for i in session.query(AdvertParserMap).filter(AdvertParserMap.is_active.is_(True),
                                                       AdvertParserMap.content_type == 2):
            AdvertParseHandler(i, session).create_adverts()
    except Exception as e:
        logging.error(f"Error in parse_advert - {e}")
    finally:
        session.close()


async def send_to_telegram(_items):
    if _items:
        session = Session()
        to_send = ""
        try:
            for item in session.query(ParsedItem).order_by(ParsedItem.created.desc()).limit(3):
                to_send = f"{to_send}<b>{json.loads(item.data).get('title', '')}</b> \n"
            for user in session.query(User).filter_by(is_subscribed=True).all():
                from bot import bot
                try:
                    private = bot.private(str(user.telegram_key))
                    await private.send_text(f"{to_send} \n<a href='https://agromega.in.ua/news/'>Докладніше</a>",
                                            parse_mode="HTML")
                except Exception as e:
                    logging.error(f'Error send to telegram - {e}. User - {user.id}')
        except Exception as e:
            logging.error(f'Error send to telegram - {e}')
        finally:
            session.close()


async def main_task():
    items = parse_items()
    await send_to_telegram(items)

    # parse adverts
    parse_links()
    parse_advert()

    # categorize parsed data
    processing()

# if __name__ == "__main__":
#     loop = asyncio.get_event_loop()
#     loop.run_until_complete(main_task())
# loop.run_until_complete(create_day_news_summary())
# asyncio.run(main_task(), debug=True)
# asyncio.run(create_day_news_summary(), debug=True)
