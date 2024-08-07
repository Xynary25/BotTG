from aiogram.utils.exceptions import ChatNotFound, BotBlocked
from loguru import logger

from aiogram import Dispatcher
from asyncio import sleep

from models import User
from data.config import ADMINS_ID


async def on_startup_notify(dp: Dispatcher):
    logger.info("Оповещение администрации...")
    for admin_id in ADMINS_ID:
        try:
            await dp.bot.send_message(admin_id, "Бот был успешно запущен", disable_notification=True)
            logger.debug(f"Сообщение отправлено {admin_id}")
        except ChatNotFound:
            logger.warning("Чат с админом не найден")
        except BotBlocked:
            logger.warning("Админ заблокировал бота")

        await sleep(0.2)


async def notify_all(dp: Dispatcher):
    logger.info("Оповещение всех пользователей...")
    for user in User.select():
        try:
            await dp.bot.send_message(user.cid, "Бот был успешно запущен")
            logger.debug(f"Сообщение отправлено {user.cid}")
        except ChatNotFound:
            logger.debug("Чат с пользователем не найден")

            await sleep(0.3)
