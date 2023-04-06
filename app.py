import asyncio

from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import BotCommand, ParseMode
from aioschedule import every, run_pending

import logging as log
import pathlib
from pydantic import BaseSettings
from colorama import Fore

import database
from database.models.lots import update_lots
from configuration import config


token = config["TOKEN"]

bot = Bot(token=token, parse_mode=ParseMode.HTML)

storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


class LoggingConfig(BaseSettings):
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "cache/logs.log"
    LOG_FORMAT: str = (
        "[%(asctime)s]:"
        "[%(levelname)-6s]:"
        "[LINE:%(lineno)-4s]:"
        "[%(name)s]:"
        "[%(filename)s]:::"
        "%(message)s"
    )
    LOG_FORMAT_COLORS: str = (
            Fore.BLUE + "[%(asctime)s]:"
            + Fore.CYAN + "[%(levelname)-6s]:"
            + Fore.WHITE + "[LINE:%(lineno)-4s]:"
            + Fore.GREEN + "[%(name)s]:"
            + Fore.MAGENTA + "[%(filename)s]:::"
            + Fore.WHITE + "%(message)s"
    )

    class Config:
        env_file = ".env"


def configure_logger():
    pathlib.Path("cache/").mkdir(exist_ok=True, parents=True)
    basic_formatter = log.Formatter(LOG_CONF.LOG_FORMAT)
    colored_formatter = log.Formatter(LOG_CONF.LOG_FORMAT_COLORS)

    file_handler = log.FileHandler(LOG_CONF.LOG_FILE)
    file_handler.setFormatter(basic_formatter)

    std_handler = log.StreamHandler()
    std_handler.setFormatter(colored_formatter)

    logger = log.getLogger()
    logger.setLevel(LOG_CONF.LOG_LEVEL)
    logger.addHandler(file_handler)
    logger.addHandler(std_handler)


LOG_CONF = LoggingConfig()
configure_logger()


async def scheduler():
    await update_lots()
    every().day.at(config['TIME_FOR_UPDATE_LOTS']).do(update_lots)
    while True:
        await run_pending()
        await asyncio.sleep(1)


async def on_startup(_):
    await bot.set_my_commands([BotCommand("start", "Запустить бота")])
    await database.init_database()
    asyncio.create_task(scheduler())


