import asyncio

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ParseMode
from loguru import logger

from qiwi import QApi
from data import config, payload

"""
Обьявление всех компонентов бота из конфига
"""

loop = asyncio.get_event_loop()

bot = Bot(config.API_TOKEN, parse_mode=ParseMode.HTML, loop=loop)
dp = Dispatcher(bot, storage=MemoryStorage())

qiwis = {}

if config.QIWI_ACCOUNTS and config.QIWI_TOKENS:
    for i in range(len(config.QIWI_ACCOUNTS)):
        qiwis[config.QIWI_ACCOUNTS[i]] = QApi(
            token=config.QIWI_TOKENS[i], account=config.QIWI_ACCOUNTS[i])

logger.info(qiwis)
