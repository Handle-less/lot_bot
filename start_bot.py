import asyncio

from aiogram import executor
from app import on_startup

from bot.handlers import dp
from database import close_database

if __name__ == "__main__":
    try:
        executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
    finally:
        asyncio.run(close_database())
