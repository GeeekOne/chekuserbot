import asyncio
import logging
import betterlogging as bl
import aiohttp

from aiogram import Bot, Dispatcher, types

from config import Config, load_config
from database.db import init_db, close_db, async_session
from utils.session import SessionMiddleware
from utils.service import scheduler
from handlers.private import private_router
from handlers.group import group_router
from handlers.posts import posts_router
from utils.bot_cmd_list import private


async def on_startup():
    """Функция запуска, инициализация БД."""
    await init_db()
    logging.info("База данных инициализирована")


async def on_shutdown(bot: Bot, session: aiohttp.ClientSession):
    """Функция завершения работы, закрытие соединений."""
    await bot.session.close()  # Закрываем сессию бота
    if not session.closed:
        await session.close()
    await close_db()  # Закрываем соединение с БД
    logging.info("Bot session and aiohttp session closed")

async def main():
    bl.basic_colorized_config(level=logging.INFO)

    config: Config = load_config('.env')
    bot = Bot(token=config.tg_bot.token)

    dp = Dispatcher()
    dp.message.middleware(SessionMiddleware())

    session = aiohttp.ClientSession()  # Создаем сессию aiohttp

    dp.workflow_data.update({
        'bot': bot,
        'group_id': config.tg_bot.group_id
        })

    dp.include_router(group_router)
    dp.include_router(private_router)
    dp.include_router(posts_router)

    await on_startup()  # Инициализируем БД перед стартом бота

    scheduler.start()
    # await bot.delete_my_commands(scope=types.BotCommandScopeAllPrivateChats())
    await bot.set_my_commands(commands=private, scope=types.BotCommandScopeAllPrivateChats())
    await bot.delete_webhook(drop_pending_updates=True)
    try:
        await dp.start_polling(bot)
    finally:
        await on_shutdown(bot, session)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Bot stopped.")
