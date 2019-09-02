import json

from aiotg import Bot, Chat

from db import Session

from settings import settings

from models.auth import User
from models.category import Category
from models.parser import ParsedItem


bot = Bot(api_token=settings.TELEGRAM_TOKEN)

session = Session()

@bot.command("/start (.+)")
async def start(chat: Chat, match):
    category = match.group(1)
    user = session.query(User).filter_by(telegram_key=str(chat.id)).first()
    if user is None:
        user = User(telegram_key=chat.id)
    if category:
        user.categories.append(session.query(Category).filter_by(id=int(category)).first())
    session.add(user)
    session.commit()
    await chat.send_text("Дякуємо! Ви успішно підписались на агроновини! Як тільки з'являться публікації вони відразу приходитимуть Вам. Для того щоб запропонувати додати Ваш улюблений ресурс до списку відслідковування, зв'яжіться з нами через форму зворотнього зв'іязку.")

# @bot.command("/getNews")
# async def get_news(chat: Chat, match):
#     user = session.query(User).filter_by(telegram_key=str(chat.id)).first()
#     for i in session.query(ParsedItem).all():
#         private = bot.private(str(user.telegram_key))
#         private.send_text(f"{json.loads(i.data)['title']} ({json.loads(i.data)['link']}", **{"parse_mode": "HTML"})

if __name__ == "__main__":
    # bot.run_webhook(webhook_url=settings.HOST + "")
    bot.run()
