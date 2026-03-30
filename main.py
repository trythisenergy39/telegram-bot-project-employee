import asyncio
import logging
from config import config
from aiogram import Bot, Dispatcher
from app.handlers import router
import psutil
import os

process = psutil.Process(os.getpid())
print(f"Использование памяти: {process.memory_info().rss / 1024 ** 2:.2f} MB")


bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()






async def main():
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')