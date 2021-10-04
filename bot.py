from aiotg import Bot, Chat

from db import Session

from settings import settings

from models.auth import User

bot = Bot(api_token=settings.TELEGRAM_TOKEN)

session = Session()


@bot.command("/start")
async def start(chat: Chat, match):
    user = session.query(User).filter_by(telegram_key=str(chat.id)).first()
    if user is None:
        user = User(telegram_key=chat.id)
    session.add(user)
    session.commit()
    await chat.send_text(
        "Дякуємо! Ви успішно підписались на агроновини! "
        "Як тільки з'являться публікації вони відразу приходитимуть Вам. "
        "Для того щоб запропонувати додати Ваш улюблений ресурс до списку відслідковування, "
        "зв'яжіться з нами через форму "
        "<a href='https://agromega.in.ua/feedback/'>зворотнього зв'язку</a>.",
        parse_mode="HTML"
    )


if __name__ == "__main__":
    bot.run()
