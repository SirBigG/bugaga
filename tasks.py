#!/usr/local/bin/python

import asyncio
import hashlib
import logging
import json
from datetime import date, datetime
from typing import Optional

import aiohttp

from sqlalchemy import func

from transliterate import slugify

from db import Session
from models.news import News

from settings import settings

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


async def generate_summary(news_titles: list[str]) -> Optional[dict]:
    prompt = "Створи підсумок за наступними заголовками новин на приблизно 500 слів: \n" + "\n".join(news_titles)
    async with aiohttp.ClientSession() as session:
        async with session.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                         "Content-Type": "application/json"},
                json={
                    "model": "gpt-4-1106-preview",
                    # "model": "gpt-3.5-turbo-1106",
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]}) as response:
            if response.status != 200:
                logging.error(f"Error generate summary from OpenAI - {response.status}: {await response.text()}.")
                return
            return await response.json()


async def create_day_news_summary(created_date: date = date.today()):
    session = Session()
    created_datetime = datetime(created_date.year, created_date.month, created_date.day, 19, 0, 0)
    try:
        # get today news
        _news = []
        for item in session.query(ParsedItem).filter(func.DATE(ParsedItem.created) == func.DATE(created_date)).all():
            if not item.data:
                continue
            _data = json.loads(item.data)
            if not _data:
                continue
            _news.append(f"{_data.get('title', '')}: {_data.get('description', '')}")
        if _news:
            _summary = await generate_summary(_news)
            if _summary and _summary.get("choices"):
                _summary = _summary.get("choices")[0].get("message", {}).get("content", "")
                if not _summary:
                    return
                # Create summary news
                _news_obj = News(
                    title=f"Підсумок новин за день {created_date}",
                    description=_summary,
                    created=created_datetime,
                )
                session.add(_news_obj)
                session.commit()
                # Create summary parsed item
                _payload = {
                    "title": f"Підсумок новин за день {created_date}",
                    "description": _summary[:100],
                    "link": f"https://agromega.in.ua/news/{slugify(_news_obj.title)}-{_news_obj.id}.html",
                }
                _parsed_item = ParsedItem(
                    data=json.dumps(_payload),
                    created=created_datetime,
                    hash=hashlib.md5(':'.join([v for _, v in _payload.items()]).encode()).hexdigest()
                )
                session.add(_parsed_item)
                session.commit()

    except Exception as e:
        logging.error(f'Save news - {e}')
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


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main_task())
    # loop.run_until_complete(create_day_news_summary())
    # asyncio.run(main_task(), debug=True)
    # asyncio.run(create_day_news_summary(), debug=True)
