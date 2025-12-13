import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from database import create_tables
from handlers import admin, user

# Logging sozlamalari
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')


async def main():
    # Baza jadvallarini yaratish (yoki mavjud bo'lsa tekshirish)
    await create_tables()

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # Routerni ulash
    dp.include_router(user.router)
    dp.include_router(admin.router)

    bot_info = await bot.get_me()
    logging.info(f"🤖 Bot ishga tushdi: @{bot_info.username}")

    # Botni ishga tushirish
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot to'xtatildi.")