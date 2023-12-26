import json
import logging
from datetime import date, datetime
from typing import Optional
import hashlib

import aiohttp

import markdown

from sqlalchemy import func

from transliterate import slugify

from db import Session
from models.news import News

from settings import settings

from models.parser import ParsedItem


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


async def create_day_news_summary(created_date: date = None):
    created_date = created_date or date.today()
    session = Session()
    created_datetime = datetime(created_date.year, created_date.month, created_date.day, 18, 0, 0)
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
                _summary_html = markdown.markdown(_summary)
                # Create summary news
                _news_obj = News(
                    title=f"Підсумок новин за день {created_date}",
                    description=_summary_html,
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
