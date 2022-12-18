# Импортируем asyncio
import asyncio

# Импортируем библиотеку для логирования
import logging

# Импорт классов и функций библиотеки aiogram
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.contrib.fsm_storage.memory import MemoryStorage

# Импортируем функцию register_commands 
from handlers.commands import register_commands

# Импортируем BOT_TOKEN 
from config import BOT_TOKEN


async def set_bot_commands(bot: Bot):
    # Функция перезапуска бота
    commands = [
        BotCommand(command="start", description="Перезапустить приложение") ]
    await bot.set_my_commands(commands)


async def main():
    """Главная функция приложения"""

    # Формируем логирование
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    # Формируем бота 
    bot = Bot(BOT_TOKEN, parse_mode="HTML")
    dp = Dispatcher(bot, storage = MemoryStorage())

    # Запускаем функцию обработки запросов
    register_commands(dp)

    await set_bot_commands(bot)

    try:
        await dp.start_polling()
    finally:
        await dp.storage.close()
        await dp.storage.wait_closed()
        await bot.session.close()

try:
    # Запуск приложения
    asyncio.run(main())
except (KeyboardInterrupt, SystemExit):
    logging.error("Bot stopped!")
