#!/usr/local/bin/python

import asyncio
import logging
import requests

from db import Session

from models.parser import ParserMap, AdvertParserMap
from models.auth import User

from parser.handlers import ParseHandler, LinkParseHandler, AdvertParseHandler

from processing import processing


def parse_items():
    session = Session()
    to_create = list()
    for i in session.query(ParserMap).filter(ParserMap.is_active == 1):
        items = ParseHandler(i, session).create_items()
        to_create.extend(items)
    # closed session finally
    session.close()
    print(f"Created {len(to_create)} items.")
    response = requests.post("https://agromega.in.ua/api/news/", json={"items": to_create})
    link = None
    if response.status_code == 200:
        link = response.json()["link"]
    return link, to_create

def parse_links():
    session = Session()
    for i in session.query(AdvertParserMap).filter(AdvertParserMap.is_active == 1, AdvertParserMap.content_type == 1):
        LinkParseHandler(i, session).create_items()
    session.close()

def parse_advert():
    session = Session()
    for i in session.query(AdvertParserMap).filter(AdvertParserMap.is_active == 1, AdvertParserMap.content_type == 2):
        AdvertParseHandler(i, session).create_adverts()
    session.close()

async def send_to_telegram(link, items):
    if link and items:
        session = Session()
        for user in session.query(User).filter_by(is_subscribed=True).all():
            from bot import bot
            try:
                private = bot.private(str(user.telegram_key))
                await private.send_text("Останні новини по Вашій підписці (%s)." % link)
            except Exception as e:
                logging.error(f'user_id : {user.telegram_key}. Error - {e}')
        session.close()

if __name__ == "__main__":
    link, items = parse_items()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(send_to_telegram(link, items))
    loop.close()

    # parse adverts
    parse_links()
    parse_advert()

    # categorize parsed data
    processing()

    # TODO: added image load