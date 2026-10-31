import asyncio
import logging
from aiogram import Bot, Dispatcher
from . import config
from .handlers import router

async def main():
    if not config.BOT_TOKEN:
        raise RuntimeError('AO3TIME_BOT_TOKEN не задан')
    logging.basicConfig(level=logging.INFO)
    bot = Bot(token=config.BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
