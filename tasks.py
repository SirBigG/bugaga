#!/usr/local/bin/python

import asyncio
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
    for i in session.query(ParserMap).filter(ParserMap.is_active.is_(True)):
        _items = ParseHandler(i, session).create_items()
        _items_count += len(_items)
    # closed session finally
    session.close()
    return _items_count


def parse_links():
    session = Session()
    for i in session.query(AdvertParserMap).filter(AdvertParserMap.is_active.is_(True), AdvertParserMap.content_type == 1):
        LinkParseHandler(i, session).create_items()
    session.close()


def parse_advert():
    session = Session()
    for i in session.query(AdvertParserMap).filter(AdvertParserMap.is_active.is_(True), AdvertParserMap.content_type == 2):
        AdvertParseHandler(i, session).create_adverts()
    session.close()


async def send_to_telegram(_items):
    if _items:
        session = Session()
        to_send = ""
        for item in session.query(ParsedItem).order_by(ParsedItem.created.desc()).limit(3):
            to_send = f"{to_send}<b>{json.loads(item.data).get('title', '')}</b> \n"
        for user in session.query(User).filter_by(is_subscribed=True).all():
            from bot import bot
            try:
                private = bot.private(str(user.telegram_key))
                await private.send_text(f"{to_send} \n<a href='https://agromega.in.ua/news/'>Докладніше</a>",
                                        parse_mode="HTML")
            except Exception as e:
                logging.error(f'user_id : {user.telegram_key}. Error - {e}')
        session.close()


def main_task():
    items = parse_items()
    asyncio.run(send_to_telegram(items))

    # parse adverts
    parse_links()
    parse_advert()

    # categorize parsed data
    processing()


if __name__ == "__main__":
    main_task()
