import asyncio

import requests

from db import Session

from models.parser import ParserMap
from models.auth import User

from parser.handlers import ParseHandler


def parse_items():
    session = Session()
    to_create = list()
    for i in session.query(ParserMap).filter(ParserMap.is_active == 1):
        items = ParseHandler(i, session).create_items()
        to_create.extend(items)
    # closed session finally
    session.close()
    response = requests.post("https://agromega.in.ua/api/news/", json={"items": to_create})
    link = None
    if response.status_code == 200:
        link = response.json()["link"]
    return link, to_create

async def send_to_telegram(link, items):
    if link and items:
        session = Session()
        for user in session.query(User).filter_by(is_subscribed=True).all():
            from bot import bot
            private = bot.private(str(user.telegram_key))
            await private.send_text("Останні новини по підписці (%s)" % link)

if __name__ == "__main__":
    link, items = parse_items()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(send_to_telegram(link, items))
    loop.close()
